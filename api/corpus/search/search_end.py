from django.http import JsonResponse

from api.corpus.initializer import corpus
from api.corpus.search.queries import filter_files_sents, filter_cat_era, appears_scanner


def filter_end_f_s(request):
    term = False
    if request.method == 'GET':
        get = request.GET
    elif request.method == 'POST':
        get = request.POST
    else:
        return JsonResponse(['ERROR: NOT GET OR POST REQUEST'], safe=False)
    if 't' in get:
        term = get['t']
    else:
        return JsonResponse(['ERROR: VARIABLE t IS NOT SPECIFIED'], safe=False)
    era = None
    category = None
    page = 1
    perpage = 10
    lemma = True
    fileid = None
    if 'era' in get:
        era = get['era']
    if 'category' in get:
        category = get['category']
    if 'fileid' in get:
        fileid = get['fileid']
    if 'page' in get:
        page = int(get['page'])
    if 'perpage' in get:
        perpage = int(get['perpage'])
    if 'lemma' in get:
        lemma = int(get['lemma'])

    if lemma:
        print('BEFORE LEMMA',term)
        term = corpus.farasa().lemmatize(term)[0]
        print('AFTER LEMMA', term)
    result = filter_files_sents(term,era,category,fileid,page,perpage,lemma)
    return JsonResponse(result,safe=False)

def filter_end_e_c(request):
    term = False
    if request.method == 'GET':
        get = request.GET
    elif request.method == 'POST':
        get = request.POST
    else:
        return JsonResponse(['ERROR: NOT GET OR POST REQUEST'], safe=False)
    if 't' in get:
        term = get['t']
    else:
        return JsonResponse(['ERROR: VARIABLE t IS NOT SPECIFIED'], safe=False)
    era = None
    category = None
    lemma = True
    if 'era' in get:
        era = get['era']
    if 'category' in get:
        category = get['category']
    if 'lemma' in get:
        lemma = int(get['lemma'])
    if lemma:
        print('BEFORE LEMMA',term)
        term = corpus.farasa().lemmatize(term)[0]
        print('AFTER LEMMA', term)
    result = filter_cat_era(term,era,category,lemma)
    return JsonResponse(result,safe=False)

def generate_word_appears(words,batch=1000,documents=None):
    for word in words:
        appears = filter_files_sents(word,perpage=batch,documents=documents)
        yield {'term':word,'appears':appears}