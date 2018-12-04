from rest_framework import viewsets, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from api.corpus import HistoricalCorpus
from api.models import Dictionary, Entry, Meaning, Period, Document
from api.serializers import DictionarySerializer, EntrySerializer, MeaningSerializer, PeriodSerializer, \
    DocumentSerializer
from pathlib import Path
from api.corpus import corpus
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


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Document.objects.all()
        categories = self.request.query_params.getlist('categories[]', [])
        periods = self.request.query_params.getlist('periods[]', [])
        query = self.request.query_params.get('query', '')
        if query:
            queryset = queryset.filter(name__contains=query)
        if categories:
            queryset = queryset.filter(category__in=categories)

        if periods:
            queryset = queryset.filter(period_id__in=periods)
        return queryset


class CategoryList(APIView):
    """
    View to list all users in the system.

    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        categories = set([doc.category for doc in Document.objects.all()])
        return Response(categories)

class PostagList(APIView):
    """
    View to list all users in the system.

    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        postags = set([meaning.posTag for meaning in Meaning.objects.all()])
        return Response(postags)

class SentenceList(APIView):
    """
    View to list all users in the system.

    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        fileid = Document.objects.get(pk=request.GET['id']).fileid
        return Response(corpus.sents(fileid))

class SentenceViewSet(viewsets.ViewSet):
    serializer_class = serializers.ListField(child=serializers.CharField())
    def get(self):
        fileid = Document.objects.get(pk=self.request.GET['id']).fileid
        return Response(corpus.sents(fileid))