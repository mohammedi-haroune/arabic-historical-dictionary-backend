from django.http import JsonResponse

from api.corpus.search.queries import filter_files_sents, filter_cat_era


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
        page = get['page']
    if 'perpage' in get:
        perpage = get['perpage']
    if 'lemma' in get:
        lemma = get['lemma']

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
        lemma = get['lemma']

    result = filter_cat_era(term,era,category,lemma)
    return JsonResponse(result,safe=False)