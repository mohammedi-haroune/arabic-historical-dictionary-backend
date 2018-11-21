from django.urls import path

from . import process

urlpatterns = [
    path('', process.means, name='means'),
]