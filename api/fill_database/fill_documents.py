import json

from django.http import HttpResponse, JsonResponse

from api.corpus.farassaWrapper.farassaInterface import Farasa
from api.fill_database import fill_models
from api.models import Corpus, Document, Period
from api.corpus.initializer import xmlDir, corpus

eras = ['Jahiliy','SadrIslam','Umayyad','Abbasid','Dual','Modern','all']
mapEraToArabic = {
    eras[0]: 'العصر الجاهلي',
    eras[1]: 'عصر صدر الإسلام',
    eras[2]: 'عصر بني أمية',
    eras[3]: 'عصر بني العباس',
    eras[4]: 'عصر الدول المتتابعة',
    eras[5]: 'العصر الحديث',
    eras[6]: "كل الأوقات"
}

mapEraToEnglish = dict((mapEraToArabic[era],era) for era in eras)

def getPeriod(periods,key):
    if key in periods:
        return periods[key]
    return None

def emptyDocuments(request):
    Document.objects.all().delete()
    return JsonResponse(['done'], safe=False)

def emptyCorpus(request):
    Corpus.objects.all().delete()
    return JsonResponse(['done'], safe=False)

def addDocuments(request):
    corp = Corpus.objects.filter(path=xmlDir,name='الجامع الاساسي')
    if not corp:
        corp = Corpus(path=xmlDir,name='الجامع الاساسي')
        corp.save()
    else:
        corp = corp[0]

    emptyDocuments(request)
    documents = json.loads(open(xmlDir+"/books_description.json").read())
    documents = corpus.booksDescription()
    periods = Period.objects.all()
    if not periods or not len(periods):
        fill_models.addPeriods(request)
        periods = Period.objects.all()
    periods = dict((mapEraToEnglish[period.name],period) for period in periods)
    # for era in eras:
    #     period = Period.objects.filter(name=mapEraToArabic[era])
    #     if not period:
    #         print('INFO FILL DOCUMENTS: LOOKING FOR ERA ' + era + " WHICH DOESN'T EXIST")
    #     else:
    #         period = period[0]
    #     periods[era] = period
    # period = Period.objects.filter(name="كل الأوقات")
    # if not period:
    #     raise Exception("couldn't find era كل الأوقات")
    # periods['all'] = period[0]
    documentsToCreateb = [Document(
        name=doc['book_name'],
        fileid=doc['fileid'],
        category=doc['type'],
        author=doc['author']['name'],
        birth_date=str(doc['author']['birth']),
        death_date=str(doc['author']['death']),
        corpus=corp,
        period=getPeriod(periods,doc['era'])) for doc in documents]
    documentsToCreate = dict((document.name,document) for document in documentsToCreateb).values()
    if len(documentsToCreate) != len(documentsToCreateb):
        print("WARNING FILL DOCUMENTS: REDUNDANT DOCUMENTS, WITH REDUNDANCY: ",len(documentsToCreateb),
              "WITHOUT REDUNDANCY: ", len(documentsToCreate))
    # for document in documentsToCreate:
    #     try:
    #         document.save()
    #     except Exception as e:
    #         print('ERROR IN FILLING DOCUMENT: ',document.name,' IS DOUBLED ', e)
    Document.objects.bulk_create(documentsToCreate)
    return HttpResponse("done!")

def testDoc(request):
    import nltk
    # path = Corpus.objects.filter(name='الجامع الاساسي')[0].path
    documents = Document.objects.all()
    documents = [(document.name,(document.fileid,document.category)) for document in documents]
    cfd = nltk.ConditionalFreqDist(documents)
    freqs = [cond for cond in cfd.keys() if len(cfd[cond]) > 1]
    res = dict((key,list(cfd[key])) for key in freqs)
    categories = list(set(list(cfd[key])[0][1] for key in freqs))
    qur = dict((key,res[key]) for key in res if res[key][0][1] == 'quran')
    # duplicated = set([(document.name,document.fileid)
    #               for d in documents
    #                 for document in documents
    #                     if document != d and document.name == d.name])
    return JsonResponse([categories,qur,res], safe=False)