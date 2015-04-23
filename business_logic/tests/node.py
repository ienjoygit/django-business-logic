# -*- coding: utf-8 -*-
#

from datetime import datetime

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import connection

from ..models import *
from utils import *


class NodeTest(TestCase):
    def test_add_root(self):
        operator = BinaryOperator(operator='+')
        operator.save()
        root = Node.add_root(content_object=operator)
        self.failUnless(root.id)
        self.failUnless(root.content_object)
        self.failUnlessEqual(operator.operator, root.content_object.operator)
        self.failUnlessEqual('+', root.content_object.operator)
        root = Node.objects.get(id=root.id)
        self.failUnless(root.content_object)
        self.failUnlessEqual(operator.operator, root.content_object.operator)
        self.failUnlessEqual('+', root.content_object.operator)


    def test_add_child(self):
        operator = BinaryOperator(operator='+')
        operator.save()
        root = Node.add_root(content_object=operator)
        self.failUnless(root.is_leaf())

        self.failUnless(root.content_object)
        self.failUnless(root.object_id)
        self.failUnlessEqual(operator.operator, root.content_object.operator)
        self.failUnlessEqual('+', root.content_object.operator)
        self.failUnlessEqual(0, len(root.get_children()))

        integer_const1 = IntegerConstant(value=1)
        child_node = root.add_child(content_object=integer_const1)
        self.failUnless(child_node.id)
        self.failUnless(child_node.content_object)

        self.failUnless(root.is_root())
        self.failUnlessEqual(1, len(root.get_children()))

        root = Node.objects.get(id=root.id)
        self.failUnlessEqual(1, len(root.get_children()))

    def test_tree(self):
        root = Node.add_root()
        self.failUnless(root.is_leaf())
        statement1 = IntegerConstant(value=33)
        statement2 = IntegerConstant(value=44)
        root = Node.objects.get(id=root.id)
        node1 = root.add_child(content_object=statement1)

        self.failUnless(node1.content_object.id)
        self.failUnless(node1.content_object.value)
        self.failUnless(node1.object_id)

        self.failUnlessEqual(node1.content_object.id, statement1.id)
        self.failUnlessEqual(node1.content_object.value, statement1.value)
        self.failUnlessEqual(node1.object_id, statement1.id)

        self.failUnless(root.pk)
        self.failUnless(statement1.pk)
        self.failUnless(root.is_root())

        root = Node.objects.get(id=root.id)
        node2 = root.add_child(content_object=statement2)
        self.failUnlessEqual(node2.content_object, statement2)

        root = Node.objects.get(id=root.id)
        children = root.get_descendants()
        self.failUnlessEqual(len(children), 2)

        child_objects = [ x.content_object for x in children ]
        self.failUnlessEqual(node1.content_object.value, child_objects[0].value)
        self.failUnlessEqual(node2.content_object.value, child_objects[1].value)

    def test_traverse(self):
        add_node = tree_1plus2mul3()
        node1, mul_node = add_node.get_children()
        node2, node3 = mul_node.get_children()

        class Visitor(NodeVisitor):
            def __init__(self):
                self.visited = []

            def visit(self, visited):
                self.visited.append(visited)

        visitor = Visitor()

        add_node.traverse(visitor)

        self.failUnlessEqual(visitor.visited,
                [add_node, node1, mul_node, node2, node3])

        class Visitor:
            def __init__(self):
                self.visited = []

            def visit(self, visited):
                self.visited.append(visited.content_object)

        visitor = Visitor()

        add_node.traverse(visitor)

        self.failUnlessEqual(visitor.visited,
                [add_node.content_object, node1.content_object,
                    mul_node.content_object, node2.content_object,
                    node3.content_object])

    def test_recursive_delete(self):
        root = Node.add_root()
        statement1 = IntegerConstant(value=1)
        statement2 = IntegerConstant(value=2)
        node1 = root.add_child(content_object=statement1)
        self.failUnlessEqual(1, len(root.get_children()))
        node2 = root.add_child(content_object=statement2)
        root = Node.objects.get(id=root.id)
        self.failUnlessEqual(2, len(root.get_children()))

        self.failUnless(IntegerConstant.objects.filter(
            pk=statement1.pk).count())
        self.failUnless(IntegerConstant.objects.filter(
            pk=statement2.pk).count())
        self.failUnless(Node.objects.filter(pk=node1.pk).count())
        self.failUnless(Node.objects.filter(pk=node2.pk).count())

        root.delete()

        self.failIf(IntegerConstant.objects.filter(pk=statement1.pk).count())
        self.failIf(IntegerConstant.objects.filter(pk=statement2.pk).count())
        self.failIf(Node.objects.filter(pk=node1.pk).count())
        self.failIf(Node.objects.filter(pk=node2.pk).count())

    def test_interpret_3(self):
        add_operator = BinaryOperator(operator='+')
        add_operator.save()
        root = Node.add_root(content_object=add_operator)

        integer_const1 = IntegerConstant(value=5)
        integer_const_node1 = root.add_child(content_object=integer_const1)

        integer_const2 = IntegerConstant(value=6)
        root = Node.objects.get(id=root.id)
        integer_const_node2 = root.add_child(content_object=integer_const2)
        root = Node.objects.get(id=root.id)

        context = Context(cache=False)
        result = root.interpret(context)

        self.failUnlessEqual(integer_const1.value  + integer_const2.value, result)

    def test_interpret_tree(self):

        add_operator = BinaryOperator(operator='+')
        add_operator.save()
        mul_operator = BinaryOperator(operator='*')

        root = Node.add_root(content_object=add_operator)

        integer_const1 = IntegerConstant(value=2)
        integer_const_node1 = root.add_child(content_object=integer_const1)

        integer_const2 = IntegerConstant(value=3)
        integer_const3 = IntegerConstant(value=4)

        mul_operator_node = root.add_child(content_object=mul_operator)
        mul_operator_node.add_child(content_object=integer_const2)
        mul_operator_node.add_child(content_object=integer_const3)

        context = Context()
        root = Node.objects.get(id=root.id)
        result = root.interpret(context)

        self.failUnlessEqual(2 + 3 * 4, result)


    def _test_long_time_interpret(self):
        #settings.DEBUG = True
        start_time = datetime.now()

        count = 16
        count = 64
        count = 256
        count = 512
        count = 1024
        count = 1024 * 8
        #count = 256
        #count = 1024 * 1024 # 1048576
        #count = 1024 * 16 # 1048576

        context = Context(cache=True)

        def calculation_time(msg):
            now = datetime.now()
            calculation_time = now - start_time
            print msg, float(calculation_time.seconds) + \
                    float(calculation_time.microseconds) / 1000000
            return now

        root = symmetric_tree(operator='+', value=1, count=count)
        start_time = calculation_time('compiling')
        compilation_queries_count = len(connection.queries)

        result = root.interpret(context)
        start_time = calculation_time('executing')

        self.failUnlessEqual(count, result)
        start_time = calculation_time('executing2')

        self.failUnlessEqual(count, result)
        for q in connection.queries[compilation_queries_count:]:
            print q['sql']
        print 'queries.count', len(connection.queries) - \
                compilation_queries_count

    def test_statement_or_block(self):
        root = Node.add_root()
        self.failUnless(root.is_block())
        self.failIf(root.is_statement())
        node1 = tree_1plus2mul3(parent=root)
        self.failUnless(root.is_block())
        self.failIf(root.is_statement())
        self.failIf(node1.is_block())
        self.failUnless(node1.is_statement())

    def test_interpret_block(self):
        root = Node.add_root()
        node1 = tree_1plus2mul3(parent=root)
        node2 = symmetric_tree(operator='*', value=5, count=4, parent=root)

        context = Context()
        result = node1.interpret(context)
        self.failUnlessEqual(7, result)

        root = Node.objects.get(id=root.id)
        context = Context()
        result = root.interpret(context)
        self.failUnlessEqual([7, 625], result)

    def test_symmetric_tree(self):
        root = symmetric_tree()
        context = Context()
        result = root.interpret(context)
        self.failUnlessEqual(2, result)
        root = symmetric_tree(operator='*', count=4, value=5)
        context = Context()
        result = root.interpret(context)
        self.failUnlessEqual(625, result)

    def test_tree_1plus2mul3(self):
        add_node = tree_1plus2mul3()
        self.failUnlessEqual(add_node.content_object.operator, '+')
        int_1node, mul_node = add_node.get_children().all()
        self.failUnlessEqual(int_1node.content_object.value, 1)
        self.failUnlessEqual(mul_node.content_object.operator, '*')
        int_2node, int_3node = mul_node.get_children().all()
        self.failUnlessEqual(int_2node.content_object.value, 2)
        self.failUnlessEqual(int_3node.content_object.value, 3)

    def test_tree_clone(self):
        root = Node.add_root()
        node1 = tree_1plus2mul3(parent=root)
        node2 = symmetric_tree(operator='*', value=5, count=4, parent=root)
        root = Node.objects.get(id=root.id)
        clone = root.clone()
        root.delete()
        self.failUnless(isinstance(clone, Node))
        self.failIf(clone.content_object)
        clone_root_children = clone.get_children()

        self.failUnlessEqual(2, len(clone_root_children))
        plus_node = clone_root_children[0]
        mul_node = clone_root_children[1]
        self.failUnless(isinstance(plus_node.content_object, BinaryOperator))
        self.failUnlessEqual('+', plus_node.content_object.operator)
        self.failUnlessEqual('*', mul_node.content_object.operator)

        context = Context()

        result = clone.interpret(context)
        self.failUnlessEqual([7, 625], result)

    def test_content_object_node_accessor(self):
        root = symmetric_tree()
        content_object = root.content_object
        self.failUnlessEqual(content_object.node, root)



class NodeCacheTest(TestCase):
    def setUp(self):
        settings.DEBUG = True
    def tearDown(self):
        settings.DEBUG = False

    def test_simple_tree_cache(self):
        queries = connection.queries
        cache_holder = NodeCacheHolder()
        node = symmetric_tree()
        not_cached_children = node.get_children().all()
        cached_children = cache_holder.get_children(node)
        self.failUnless(isinstance(cache_holder._node_cache, NodeCache))
        for i, child in enumerate(not_cached_children):
            self.failUnlessEqual(child.id, cached_children[i].id)
        max_num_queries = len(queries)
        self.failUnlessEqual(max_num_queries, len(queries))
        content_object = node.content_object
        self.failUnlessEqual(max_num_queries, len(queries))
        content_object = cached_children[0].content_object
        self.failUnlessEqual(max_num_queries, len(queries))
        content_object = cached_children[1].content_object
        self.failUnlessEqual(max_num_queries, len(queries))

    def test_init_node_in_cache(self):
        cache_holder = NodeCacheHolder()
        node = symmetric_tree()
        cached_children = cache_holder.get_children(node)
        self.failUnless(node is cache_holder._node_cache._node_by_id[node.id])

    def test_medium_tree_cache(self):
        queries = connection.queries
        cache_holder = NodeCacheHolder()
        node = symmetric_tree(count=4)
        lft_mul_node, rgh_mul_node = node.get_children().all()
        lft_lft_child, rgh_lft_child = lft_mul_node.get_children().all()
        lft_rgh_child, rgh_rgh_child = rgh_mul_node.get_children().all()
        cached_lft_mul_node, cached_rgh_mul_node = \
                cache_holder.get_children(node)

        max_num_queries = len(queries)
        cached_lft_lft_child, cached_rgh_lft_child = \
                cache_holder.get_children(cached_lft_mul_node)
        cached_lft_rgh_child, cached_rgh_rgh_child = \
                cache_holder.get_children(cached_rgh_mul_node)
        self.failUnlessEqual(max_num_queries, len(queries))
        cached_lft_rgh_child, cached_rgh_rgh_child = \
                cache_holder.get_children(rgh_mul_node)
        content_object = cached_rgh_mul_node.content_object
        content_object = cached_lft_rgh_child.content_object
        content_object = cached_rgh_rgh_child.content_object
        self.failUnlessEqual(max_num_queries, len(queries))

    def test_content_object_node_accessor(self):
        queries = connection.queries
        cache_holder = NodeCacheHolder()
        root = symmetric_tree()
        cache_holder.get_children(root)
        max_num_queries = len(queries)
        content_object = root.content_object
        self.failUnless(content_object.node is root)
        self.failUnlessEqual(max_num_queries, len(queries))

