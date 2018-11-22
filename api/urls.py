from django.urls import path

from api.fill_database import fill_wassit
from . import process

urlpatterns = [
    path('', process.means, name='means'),
    path('wassit',fill_wassit.addWassit, name='wassit'),
    path('entries',fill_wassit.entries,name='entries')
]