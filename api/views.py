from django.shortcuts import render
from rest_framework import viewsets
from api.serializers import DictionarySerializer, EntrySerializer, MeaningSerializer
from api.models import Dictionary, Entry, Meaning
# Create your views here.


# ViewSets define the view behavior.
class DictionaryViewSet(viewsets.ModelViewSet):
    queryset = Dictionary.objects.all()
    serializer_class = DictionarySerializer

class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer


class MeaningViewSet(viewsets.ModelViewSet):
    queryset = Meaning.objects.all()
    serializer_class = MeaningSerializer
