from django.urls import path

from api.fill_database import fill_wassit, fill_models, fill_documents
from api.fill_database import fill_maany
from . import process

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers
from api.views import DictionaryViewSet, EntryViewSet, MeaningViewSet, PeriodViewSet, CategoryList, DocumentViewSet, \
    PostagList, SentenceList, SentenceViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'dictionaries', DictionaryViewSet)
router.register(r'entries', EntryViewSet)
router.register(r'meanings', MeaningViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'documents', DocumentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('wassit',fill_wassit.addWassit, name='wassit'),
    path('entries',fill_maany.entries,name='entries'),
    path('maany', fill_maany.addMaany, name='maany'),
    path('periods', fill_models.addPeriods, name='periods'),
    path('fill/documents', fill_documents.addDocuments, name='documents'),
    path('testDoc',fill_documents.testDoc, name='testDoc'),
    path('categories/', CategoryList.as_view()),
    path('postags/', PostagList.as_view()),
    #path('sentences/', SentenceList.as_view()),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]