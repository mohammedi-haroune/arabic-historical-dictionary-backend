import inspect
import json
import os
import random
from json.decoder import WHITESPACE

import django
from django.core.paginator import Paginator
from django.db import connection

from api.fill_database.fill_documents import mapEraToArabic
from api.models import Entry, Appears, Document, WordAppear, Meaning, Period

try: from xml.etree import cElementTree as ET
except ImportError: from xml.etree import ElementTree as ET
from django.http import JsonResponse

from api.corpus.initializer import corpus

def export_dict_Xml(request):
    refresh = False
    if request.method == 'GET':
        get = request.GET
        if 'refresh' in get:
            refresh = get['refresh'][0]
    stats = getGlobalStatistics(refresh)
    root = ET.Element("historical_dict",encoding='utf-8')
    metaData = ET.SubElement(root,'global_info')
    num_terms = ET.SubElement(metaData, 'num_terms').text = str(stats['number_of_terms'])
    ET.SubElement(metaData, 'num_docs').text = str(stats['number_of_docs'])
    ET.SubElement(metaData, 'num_examples').text = str(stats['total_registered_appears'])
    apps = genAppears()
    prev = None
    print("INFO EXPORT XML: LOADING ENTRIES...")
    entries = Entry.objects.all()
    entries = dict((entry.pk, entry) for entry in entries)
    ents = ET.SubElement(root, 'entries')
    means = {}
    app = []
    countm = 1
    count = 0
    for appears in apps:
        meaning = appears.meaning
        entry = entries[meaning.entry_id]
        print("INFO EXPORT XML: NEW APPEAR", entry.term, prev)
        if entry.term != prev:
            if prev is not None:
                entry_tag = ET.SubElement(ents, 'entry', term=prev)
                means_tag = ET.SubElement(entry_tag, 'meanings')
                for i,m in sorted(means.values(),key=lambda x:x[0]):
                    ET.SubElement(means_tag, 'm', postag=m.posTag, id=str(i)).text = m.text
                exam_tag = ET.SubElement(entry_tag, 'examples')
                for a in app:
                    appears2 = a['appears']
                    atag = ET.SubElement(exam_tag, 'a', meaning_id=str(a['m']),
                                         sentence=str(appears2.position),
                                 word_pos=str(appears2.word_position))
                    ET.SubElement(atag,'doc').text = appears2.document.fileid
                    ET.SubElement(atag,'sample_text').text = appears2.sentence
                    ET.SubElement(atag,'confirmed').text = str(appears2.confirmed)
                count += 1
                print("INFO EXPORT XML: ADDED ENTRY", count)
            means = {}
            app = []
            countm = 0
            prev = entry.term
        if meaning.pk not in means:
            means[meaning.pk] = (countm,meaning)
            countm += 1

        app.append({'m':means[meaning.pk][0],'appears':appears})
    if len(app):
        entry_tag = ET.SubElement(ents, 'entry', term=entry.term)
        means_tag = ET.SubElement(entry_tag, 'meanings')
        for i, m in sorted(means.values(), key=lambda x: x[0]):
            ET.SubElement(means_tag, 'm', postag=m.posTag, id=str(i)).text = m.text
        exam_tag = ET.SubElement(entry_tag, 'examples')
        for a in app:
            appears = a['appears']
            atag = ET.SubElement(exam_tag, 'a', meaning_id=str(a['m']), sentence=str(appears.position),
                                 word_pos=str(appears.word_position))
            ET.SubElement(atag, 'doc').text = appears.document.fileid
            ET.SubElement(atag, 'sample_text').text = appears.sentence
            ET.SubElement(atag, 'confirmed').text = str(appears.confirmed)
        count += 1
        print("INFO EXPORT XML: ADDED ENTRY", count)
            # print(str(len(sentences)))

    num_terms = count
    tree = ET.ElementTree(root)
    filepath = "historical_dict.xml"
    tree.write(filepath)
    return JsonResponse(['done'],safe=False)

def genAppears(batch=10000):
    paginator = Paginator(Appears.objects.select_related().all()
                          .order_by('meaning__entry'),batch)
    for p in paginator.page_range:

        print("INFO: LOADING APPEARS PAGE ",p)
        for appear in paginator.get_page(p):

            yield appear

def getWordStatistics(request):
    # categories = dict((e, dict((c, 0) for c in corpus.categories())) for e in corpus.eras())
    get = {}
    if request.method == 'GET':
        get = request.GET
        if 'id' not in get:
            return JsonResponse({}, safe=False)
    elif request.method == 'POST':
        get = request.POST
        if 'id' not in get:
            return JsonResponse({}, safe=False)
    word = get['id']
    print("INFO GET STATISTICS: GETTING WORD'S MEANINGS APPEARS...", word)
    apps = Appears.objects.select_related().filter(meaning__entry__id=word)
    if not apps:
        return JsonResponse({},safe=False)
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
    doc_stats = dict((mapEraToArabic[e], dict((c, 0) for c in corpus.categories()))
                 for e in corpus.eras())
    print("INFO GET STATISTICS: LOADING DOCUMENTS...")
    documents = Document.objects.all()
    documents = dict((document.pk, document) for document in documents)
    for document in documents.values():
        category = document.category
        era = periods[document.period_id].name
        doc_stats[era][category] += 1
    count = 0
    for appears in apps:
        document = documents[appears.document_id]
        category = document.category
        era = periods[document.period_id].name
        stats[era][category] += 1
        count += 1
        print("INFO GET STATISTICS: ADDED APPEAR TO STATS...",count)
    global_stats = {
        'number_of_docs': len(documents),
        'number_of_terms': len(Entry.objects.all()),
        'total_registered_appears': count,
        'doc_stats': doc_stats,
        'appears_stats': stats
    }
    print(django.db.connection.queries)
    with open(file, 'w') as fp:
        json.dump(global_stats, fp)
    print('INFO GET STATISTICS: FINISHED REFRESHING')
    return global_stats
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

def getWordAppears(request):
    print(request.GET)
    limit = 5
    if request and request.method == 'GET':
        get = request.GET
        if 't' not in get:
            return JsonResponse([],safe=False)
        if 'limit' in get:
            limit = int(get['limit'])
    else:
        return JsonResponse([],safe=False)

    word = get['t']
    print("INFO WORD APPARITION: LOADING APPARITIONS FOR ", word)
    apps = corpus.word_apparitions_gen({word}, lemma=False, limitByFile=limit)
    docs = [corpus.getFileIdFromId(value['file_id']) for w,value in apps]
    return JsonResponse(docs,safe=False)

def fillWordApps(batch=10000,lemma=False):
    emptyWordAppears(None)
    print("INFO FILL WORD APPEARS: LOADING ENTRIES...")
    entries = Entry.objects.all()
    entries = dict((entry.term, entry) for entry in entries)
    print("INFO FILL WORD APPEARS: LOADING DOCUMENTS...")
    documents = Document.objects.all()
    documents = dict((document.fileid, document) for document in documents)
    entrieset = entries.keys()
    apps = corpus.word_apparitions_gen(entrieset, get_sentences=True,lemma=lemma,
                                       limit=1)

    appears = []
    count = 0
    print("INFO FILL WORD APPEARS: STARTS FILLING...")
    for w, value in apps:
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
            if count % 10000 == 0:
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

def fillWordAppears(request):
    batch = 10000
    lemma = True
    if request and request.method == 'GET':
        get = request.GET
        if 'batch' in get:
            batch = get['batch'][0]
    return fillWordApps(batch,lemma)


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

def fillHistoric(batch=10000):

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
        if len(appears) > batch:
            Appears.objects.bulk_create(appears)
            appears = []
            print('INFO FILL HISTORIC DICT: APPEAR CREATED BULK')

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