from django.urls import path

from api.fill_database import fill_wassit, fill_models, fill_documents, historicalDict, fill_dicos
from api.fill_database import fill_maany
from api.serializers import MeaningAppearsSerializer
from . import process

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers
from api.views import DictionaryViewSet, EntryViewSet, MeaningViewSet, PeriodViewSet, CategoryList, DocumentViewSet, \
    PostagList, SentenceList, SentenceViewSet, AppearsViewSet, MeaningApperasViewSet, WordAppearsViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'dictionaries', DictionaryViewSet)
router.register(r'entries', EntryViewSet)
router.register(r'meanings', MeaningViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'appears', AppearsViewSet)
router.register(r'meaning_appears', MeaningApperasViewSet)
router.register(r'word_appears', WordAppearsViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('entries', fill_maany.entries, name='entries'),
    path('export/xml', historicalDict.export_dict_Xml, name='entries'),
    #api/statistics to get global statistics set ?refresh=1 to refresh statistics
    path('statistics', historicalDict.getStatistics, name='stats'),
    #api/statistics/word?term=t1 to get statistics regarding t1's meanings
    path('statistics/word',historicalDict.getWordStatistics,name='word_stats'),
    path('delete/appears', historicalDict.emptyAppears, name='delete_word_appears'),
    path('delete/wordAppears', historicalDict.emptyWordAppears, name='delete_appears'),
    path('delete/documents', fill_documents.emptyDocuments, name='delete_documents'),
    path('delete/corpus', fill_documents.emptyCorpus, name='delete_corpus'),
    path('fill/periods', fill_models.addPeriods, name='periods'),
    path('fill/historicDict', historicalDict.fillHistoricDict, name='historicDict'),
    path('fill/wordAppears', historicalDict.fillWordAppears, name='wordAppears'),
    path('fill/documents', fill_documents.addDocuments, name='documents'),
    path('fill/dico/maany', fill_maany.maany, name='maany'),
    path('fill/dico/wassit', fill_dicos.wassit, name='wassit'),
    path('fill/dico/alghni', fill_dicos.elghani, name='elghani'),
    path('fill/dico/alraeid', fill_dicos.elraeid, name='elraeid'),
    path('testDoc', fill_documents.testDoc, name='testDoc'),
    path('apparition/word',historicalDict.getWordAppears, name='word_appears'),
    path('categories/', CategoryList.as_view()),
    path('postags/', PostagList.as_view()),
    path('sentences/', SentenceViewSet.as_view({'get': 'list'})),
    #path('sentences/', SentenceList.as_view()),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]