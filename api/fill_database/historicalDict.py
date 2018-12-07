from django.http import JsonResponse

from api.corpus.initializer import corpus
from api.models import Dictionary, Entry


def createXmlDict(request):
    dictionary = Dictionary.objects.filter(name='المعجم الوسيط')[0]
    entries = Entry.objects.filter(dictionary=dictionary)
    entries = [entry.term for entry in entries]
    apps = corpus.words_apparitions(set(entries))
    return JsonResponse(apps,safe=False)