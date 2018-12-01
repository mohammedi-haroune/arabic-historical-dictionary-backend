import json

from django.http import HttpResponse, JsonResponse

from api.corpus.HistoricalCorpus import HistoricalCorpus
from api.models import Corpus, Document, Period
from api.corpus.initializer import xmlDir, eras, mapEraToArabic


def addDocuments(request):
    corpus = Corpus.objects.filter(path=xmlDir,name='الجامع الاساسي')
    if not corpus:
        corpus = Corpus(path=xmlDir,name='الجامع الاساسي')
        corpus.save()
    else:
        corpus = corpus[0]

    documents = json.loads(open(xmlDir+"/books_description.json").read())
    periods = {}
    for era in eras:
        period = Period.objects.filter(name=mapEraToArabic[era])
        if not period:
            raise Exception('looking for era' + era + "which doesn't exist")
        else:
            period = period[0]
        periods[era] = period
    documentsToCreate = [Document(
        name=doc['book_name'],
        fileid=doc['fileid'],
        category=doc['type'] ,
        author=doc['author']['name'],
        birth_date=str(doc['author']['birth']),
        death_date=str(doc['author']['death']),
        corpus=corpus,
        period=periods[doc['era']]) for doc in documents]

    meaningsToCreate = []
    Document.objects.bulk_create(documentsToCreate)
    return HttpResponse("done!")

def testDoc(request):
    path = Corpus.objects.filter(name='الجامع الاساسي')[0].path
    corpus = HistoricalCorpus(path)
    return JsonResponse(corpus.sents(corpus.fileids()[0])[:100], safe=False)