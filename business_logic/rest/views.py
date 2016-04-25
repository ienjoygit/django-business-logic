# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.filters import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

from rest_framework.decorators import api_view
from rest_framework import generics, exceptions
from rest_framework.response import Response

from .serializers import *


def format_url(_url):
    return 'business-logic:rest:{}'.format(_url)


@api_view(('GET',))
def api_root(request, format=None):
    from rest_framework.reverse import reverse

    return Response(OrderedDict((
        ('program-type', reverse(format_url('program-type-list'), request=request, format=format)),
        ('program', reverse(format_url('program-list'), request=request, format=format)),
        ('program-version', reverse(format_url('program-version-list'), request=request, format=format)),
        ('reference-descriptor', reverse(format_url('reference-descriptor-list'), request=request, format=format)),
    )))


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProgramTypeList(generics.ListAPIView):
    queryset = ProgramType.objects.all()
    serializer_class = ProgramTypeListSerializer
    pagination_class = StandardResultsSetPagination


class ProgramTypeView(generics.RetrieveAPIView):
    queryset = ProgramType.objects.all()
    serializer_class = ProgramTypeSerializer


class ProgramList(generics.ListAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('program_type', )


class ProgramVersionList(generics.ListCreateAPIView):
    queryset = ProgramVersion.objects.all()
    serializer_class = ProgramVersionListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('program', )


class ProgramVersionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProgramVersion.objects.all()
    serializer_class = ProgramVersionSerializer


class ReferenceDescriptorList(generics.ListAPIView):
    queryset = ReferenceDescriptor.objects.all()
    serializer_class = ReferenceDescriptorListSerializer

class ReferenceList(generics.ListAPIView):
    serializer_class = ReferenceListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.get_reference_model().objects.all()

    def get_reference_model(self):
        try:
            app_name, model_name = self.kwargs['model'].split('.')
            model = get_model(app_name, model_name)
            ReferenceDescriptor.objects.get(content_type=ContentType.objects.get_for_model(model))
        except (ValueError, LookupError, ReferenceDescriptor.DoesNotExist):
            raise exceptions.NotFound()

        return model
