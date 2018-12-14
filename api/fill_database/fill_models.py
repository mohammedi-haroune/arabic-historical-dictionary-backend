import json

from django.http import HttpResponse

from api.models import Period, Document, Corpus
from random import randint

def addPeriods(request):
    periods = json.loads(open("api/fill_database/periods2.json").read())

    print(periods)

    periodsToCreate = [Period(name=word['name'],
                              start=word['start'],
                              end=word['end'],
                              description=word['description']) for word in periods]

    print(periodsToCreate)

    Period.objects.bulk_create(periodsToCreate)
    return HttpResponse("done!")


def addDocuments():
    documents = json.loads(open("api/fill_database/documents.json").read())

    print(documents)

    documentsToCreate = [Document(name=doc['name'],
                                  path=doc['path'],
                                  category=doc['category'],
                                  author=doc['author'],
                                  description=doc['description'],
                                  corpus=Corpus.objects.first(),
                                  period=Period.objects.all()[randint(0, len(Period.objects.all()) - 1)])
                         for doc in documents]

    print(documentsToCreate)

    Document.objects.bulk_create(documentsToCreate)