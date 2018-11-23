from django.urls import path

from api.fill_database import fill_wassit
from . import process

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers
from api.views import DictionaryViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'dictionaries', DictionaryViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('wassit',fill_wassit.addWassit, name='wassit'),
    path('entries',fill_wassit.entries,name='entries'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]