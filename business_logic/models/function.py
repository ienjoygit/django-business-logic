# -*- coding: utf-8 -*-
#

from importlib import import_module

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel


@python_2_unicode_compatible
class FunctionDefinition(PolymorphicModel):
    title = models.CharField(_('Function title'), max_length=255, unique=True)
    is_context_required = models.BooleanField(_('Is Context required'), default=False)
    is_returns_value = models.BooleanField(_('Is returns value'), default=True)

    def __str__(self):
        return self.title

    def call(self, context, *args):
        raise NotImplementedError()


@python_2_unicode_compatible
class FunctionArgument(models.Model):
    function = models.ForeignKey(FunctionDefinition, related_name='arguments')
    name = models.CharField(max_length=255, null=True, blank=True)

    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = _('Function argument')
        verbose_name_plural = _('Function arguments')

        ordering = ('order', )

    def __str__(self):
        return self.name or '*'


class PythonModuleFunctionDefinition(FunctionDefinition):
    module = models.CharField(_('Module name'), max_length=255, default='__builtins__')
    function = models.CharField(_('Function name'), max_length=255)

    class Meta:
        verbose_name = _('Python module function definition')
        verbose_name_plural = _('Python module function definition')

    def interpret(self, context, *args):
        pass

    def call(self, context, *args):
        if not self.module or self.module == '__builtins__':
            code = __builtins__[self.function]
        else:
            module = import_module(self.module)
            code = getattr(module, self.function)
        if self.is_context_required:
            return code(context, *args)
        return code(*args)


class PythonCodeFunctionDefinition(FunctionDefinition):
    code = models.TextField(_('Code'), max_length=255)

    class Meta:
        verbose_name = _('Python code function definition')
        verbose_name_plural = _('Python code function definition')

    def interpret(self, context, *args):
        pass

    def call(self, context, *args):
        locals = dict(arg=args[0], ret=None)
        code = compile('''{}
ret = function(arg)
'''.format(self.code), '<string>', 'exec')
        try:
            eval(code, {}, locals)
        except Exception as e:
            print(e)
        return locals['ret']


@python_2_unicode_compatible
class FunctionLibrary(models.Model):
    title = models.CharField(_('Function library title'), max_length=255, unique=True)
    functions = models.ManyToManyField('FunctionDefinition', related_name='libraries')

    class Meta:
        verbose_name = _('Function library')
        verbose_name_plural = _('Function libraries')

    def __str__(self):
        return self.title


class Function(models.Model):
    definition = models.ForeignKey('FunctionDefinition', related_name='functions')

    class Meta:
        verbose_name = _('Function')
        verbose_name_plural = _('Functions')

    def interpret(self, context, *args):
        return self.definition.call(context, *args)


