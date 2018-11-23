from django.shortcuts import render
from rest_framework import viewsets
from api.serializers import DictionarySerializer
from api.models import Dictionary
# Create your views here.


# ViewSets define the view behavior.
class DictionaryViewSet(viewsets.ModelViewSet):
    queryset = Dictionary.objects.all()
    serializer_class = DictionarySerializer
