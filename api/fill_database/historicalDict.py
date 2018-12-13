import inspect
import json
import os
import random
from json.decoder import WHITESPACE

from django.core.paginator import Paginator
from django.db import connection

from api.fill_database.fill_documents import mapEraToArabic
from api.models import Entry, Appears, Document, WordAppear, Meaning, Period

try: from xml.etree import cElementTree as ET
except ImportError: from xml.etree import ElementTree as ET
from django.http import JsonResponse

from api.corpus.initializer import corpus

def _createXml(path,name,author,type,savePath,era,id):
    root = ET.Element("root",encoding='utf-8')
    metaData = ET.SubElement(root,'statistics')
    ET.SubElement(metaData, 'number_of_terms').text = name
    ET.SubElement(metaData, 'era').text = era
    auth = ET.SubElement(metaData, 'author')
    ET.SubElement(auth, 'name').text = author['name']
    ET.SubElement(auth, 'birth').text = str(author['birth'])
    ET.SubElement(auth, 'death').text = str(author['death'])
    ET.SubElement(metaData,'id').text = str(id)
    ET.SubElement(metaData, 'type').text = type


    # print(str(len(sentences)))


    tree = ET.ElementTree(root)
    savePath = savePath+'/'+type
    filepath = savePath+'/'+name+".xml"
    tree.write(filepath)
    return filepath

def genAppears(batch=50000):
    paginator = Paginator(Appears.objects.select_related().all(),batch)
    for p in paginator.page_range:
        print("INFO: LOADING APPEARS PAGE ",p)
        for appear in paginator.get_page(p):
            yield appear

def getWordStatistics(request):
    # categories = dict((e, dict((c, 0) for c in corpus.categories())) for e in corpus.eras())
    get = {}
    if request.method == 'GET':
        get = request.GET
        if 'term' not in get:
            return {}
    elif request.method == 'POST':
        get = request.POST
        if 'term' not in get:
            return {}
    word = get['term']
    print("INFO GET STATISTICS: GETTING WORD'S MEANINGS APPEARS...", word)
    apps = Appears.objects.select_related().filter(meaning__entry__term=word)
    print("INFO GET STATISTICS: LOADING PERIODS...")
    periods = Period.objects.all()
    periods = dict((period.pk, period) for period in periods)
    word_stats = {}
    count = 0
    for appears in apps:
        meaning = appears.meaning
        if meaning.pk not in word_stats:
            word_stats[meaning.pk] = {'meaning': meaning.text,
                                      'stats': dict((mapEraToArabic[e], dict((c, 0)
                                        for c in corpus.categories()))
                                            for e in corpus.eras())}
        document = appears.document
        category = document.category
        era = periods[document.period_id].name
        word_stats[meaning.pk]['stats'][era][category] += 1
        count += 1
        print("INFO GET STATISTICS: ADDED APPEAR TO STATS...",count)
    return JsonResponse(word_stats,safe=False)

def getGlobalStatistics(refresh=False):
    root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    file = root + '/global_stats.json'
    if not refresh and os.path.isfile(file):
        print('INFO GET STATISTICS: NOT REFRESHING')
        return json.loads(open(file).read())
    print('INFO GET STATISTICS: REFRESHING')
    apps = genAppears()
    print("INFO GET STATISTICS: LOADING PERIODS...")
    periods = Period.objects.all()
    periods = dict((period.pk, period) for period in periods)
    stats = dict((mapEraToArabic[e], dict((c, 0) for c in corpus.categories()))
                                        for e in corpus.eras())
    print("INFO GET STATISTICS: LOADING DOCUMENTS...")
    documents = Document.objects.all()
    documents = dict((document.pk, document) for document in documents)
    count = 0
    for appears in apps:
        document = documents[appears.document_id]
        category = document.category
        era = periods[document.period_id].name
        stats[era][category] += 1
        count += 1
        print("INFO GET STATISTICS: ADDED APPEAR TO STATS...",count)
    with open(file, 'w') as fp:
        json.dump(stats, fp)
    print('INFO GET STATISTICS: FINISHED REFRESHING')
    return stats
def getStatistics(request):
    refresh = False
    if request.method == 'GET':
        get = request.GET
        if 'refresh' in get:
            refresh = get['refresh'][0]
    stats = getGlobalStatistics(refresh)
    return JsonResponse(stats,safe=False)



def emptyAppears(request):
    Appears.objects.all().delete()
    return JsonResponse(['done'],safe=False)

def emptyWordAppears(request):
    WordAppear.objects.all().delete()
    return JsonResponse(['done'], safe=False)

def fillWordAppears(request):
    batch = 10000
    if request.method == 'GET':
        get = request.GET
        if 'batch' in get:
            batch = get['batch'][0]
    emptyWordAppears(request)
    print("INFO FILL WORD APPEARS: LOADING ENTRIES...")
    entries = Entry.objects.all()
    entries = dict((entry.term, entry) for entry in entries)
    print("INFO FILL WORD APPEARS: LOADING DOCUMENTS...")
    documents = Document.objects.all()
    documents = dict((document.fileid, document) for document in documents)
    entrieset = entries.keys()
    apps = corpus.word_apparitions_gen(entrieset, get_sentences=True)


    appears = []
    count = 0
    print("INFO FILL WORD APPEARS: STARTS FILLING...")
    for w,value in apps:
        entry = entries[w]
        fileid = corpus.getFileIdFromId(value['file_id'])

        if fileid not in documents:
            print("WARNING FILL WORD APPEARS: DOCUMENT EXISTS IN CORPUS BUT NOT IN DATABASE")
            continue
        document = documents[fileid]
        try:
            sentence = value['sentence']
            appears.append(WordAppear(
                sentence=sentence,
                position=value['sentence_pos'],
                word_position=value['word_pos'],
                document=document,
                entry=entry
            ))

            count += 1
            print('INFO FILL WORD APPEARS: APPEAR APPENDED', count)
        except Exception as e:
            print("ERROR FILL WORD APPEARS: ENTRY WITHOUT MEANING", entry, e)
            print(document, entry)
            print(value['sentence_pos'], value['word_pos'])

        if len(appears) < batch:
            continue
        WordAppear.objects.bulk_create(appears)
        appears = []
        print('INFO FILL WORD APPEARS: WORDAPPEAR CREATED BULK')

    if len(appears):
        WordAppear.objects.bulk_create(appears)
        print('INFO FILL WORD APPEARS: WORDAPPEAR CREATED BULK')
    return JsonResponse(['done'], safe=False)


def fillHistoricDict(request):
    emptyAppears(request=request)
    refresh = False
    if request.method == 'GET':
        get = request.GET
        if 'refresh' in get:
            refresh = get['refresh'][0]

    return fillHistoric()

def genWordAppears(batch=10000):
    paginator = Paginator(WordAppear.objects.all(),batch)
    for p in paginator.page_range:
        print("INFO: LOADING APPEARS PAGE ",p)
        for appear in paginator.get_page(p):
            yield appear

def fillHistoric():

    # entries = json.loads(open("api/fill_database/dicts/wassit.json").read())
    print("INFO FILL HISTORIC DICT: LOADING DOCUMENTS...")
    documents = Document.objects.all()
    documents = dict((document.pk, document) for document in documents)
    print("INFO FILL HISTORIC DICT: LOADING MEANINGS...")
    meaningsql = Meaning.objects.all()
    meanings = {}
    count = 0
    for meaning in meaningsql:
        count += 1
        # print("INFO FILL HISTORIC DICT: LOADING MEANINGS...", count)
        if meaning.entry_id in meanings:
            meanings[meaning.entry_id].append(meaning)
        else:
            meanings[meaning.entry_id] = [meaning]
    appears = []
    count = 0

    for wordAppear in genWordAppears():
        # print(connection.queries[-1])
        if wordAppear.entry_id not in meanings:
            print("WARNING FILL HISTORIC DICT: ENTRY IN APPEAR NOT IN MEANING", wordAppear.entry_id)
            continue
        means = meanings[wordAppear.entry_id]
        meaning = means[random.randrange(0,len(means))]
        document = documents[wordAppear.document_id]
        appears.append(Appears(
            sentence=wordAppear.sentence,
            position=wordAppear.position,
            word_position=wordAppear.word_position,
            document=document,
            meaning=meaning
        ))
        count += 1
        print('INFO FILL HISTORIC DICT: APPEAR APPENDED ', count)

    if len(appears):
        Appears.objects.bulk_create(appears)
        print('INFO FILL HISTORIC DICT: APPEAR CREATED BULK')
    return JsonResponse(['done'],safe=False)

def getAppearances(get_sents,refresh=False):

    root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    file = root+'/apps'
    if get_sents:
        file += '_sents'
    file += '.json'
    if not refresh and os.path.isfile(file):
        print('INFO FILL HISTORIC DICT: NOT REFRESHING')
        return json.loads(open(file).read())
    print('INFO FILL HISTORIC DICT: REFRESHING')
    entries = json.loads(open("api/fill_database/dicts/wassit.json").read())
    entries = entries.keys()
    apps = corpus.words_apparitions(set(entries), get_sentences=get_sents)
    with open(file, 'w') as fp:
        json.dump(apps, fp)
    print('INFO FILL HISTORIC DICT: FINISHED REFRESHING')
    return apps

if __name__ == '__main__':
    apps = getAppearances(True)
    print(len(apps))