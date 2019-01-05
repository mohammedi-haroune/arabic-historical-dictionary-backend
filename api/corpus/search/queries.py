from django.http import JsonResponse
from elasticsearch.helpers import scan

from api.corpus.initializer import corpus
from api.corpus.search.common import connect_elasticsearch, get_sentence_index_name
from api.fill_database.fill_documents import mapEraToArabic, mapEraToEnglish
from api.models import Document

def get_sentence(fileid,position,term,lemma_sentence):
    sent = corpus.sents(fileid, position + 1, position + 1)[0]
    if term not in lemma_sentence:
        print('WARNING: TERM NOT IN LEMMA SENTENCE')
        return sent,-1
    context_size = 5
    if len(sent) <= context_size*2+1:
        return sent,lemma_sentence.index(term)
    i = lemma_sentence.index(term)
    low = max([0,i-context_size])
    high = min([len(sent),i+context_size])
    # to fix sent size to 10 tokens
    addH = max([0,context_size-i])
    addL = max(0,i+context_size-len(sent))
    sent = sent[low-addL:high+addH]
    return sent,context_size-addH

def appears_scanner(term,batch=5000,documents=None,lemma=True):
    es = connect_elasticsearch()
    index = get_sentence_index_name(lemma)
    query = {
        "query": {
            "bool":
                {
                    "filter": [
                        {"term": {"sentence": term}}
                    ]
                }
        }
    }
    hit_gen = scan(es,index=index, query=query,size=batch)
    result = []
    for res in hit_gen:
        src = res['_source']
        position = src['position']
        fileid = src['parent']

        # TODO FIX FILEID IN ELASTICSEARCH SERVER
        fileid = '/'.join(fileid.split('/')[1:])
        if documents:
            if fileid in documents:
                document = documents[fileid]
            else:
                continue
        else:
            document = Document.objects.filter(fileid=fileid)
            if document:
                document = document[0]
            else:
                continue
        sent, word_pos = get_sentence(fileid, position, term, src['sentence'])
        # sent = src['sentence']
        result.append({
            'document': document.id,
            # 'lemma_sentence': src['sentence'],
            'sentence': sent,
            'word_position': word_pos,
            'position': src['position']

        })
        if len(result) >= batch:
            yield result
            result = []
    if len(result):
        yield result


def filter_files_sents(term,era=None,category=None,fileid=None,page=1,perpage=20,
                       lemma=True,documents=None):
    es = connect_elasticsearch()
    index = get_sentence_index_name(lemma)
    start = (page-1)*perpage
    query = {
        "from":start,"size":perpage,
        "query":{
            "bool":
                {
                    "filter":[
                        {"term": {"sentence": term}}
                    ]
                }
        }
    }
    if era:
        if era in mapEraToEnglish:
            era = mapEraToEnglish[era]
        elif era not in mapEraToArabic:
            raise Exception('era does not exist')
        query['query']['bool']['filter'].append({"term":{"era":era}})
    if category:
        query['query']['bool']['filter'].append({"term":{"category":category}})
    if fileid:
        print('fileid is',fileid)
        query['query']['bool']['filter'].append({"term":{"parent":fileid}})
    r = es.search(index=index,body=query)
    r = r['hits']['hits']
    result = []
    for res in r:
        src = res['_source']
        position = src['position']
        fileid = src['parent']

        # TODO FIX FILEID IN ELASTICSEARCH SERVER
        fileid = '/'.join(fileid.split('/')[1:])
        if documents:
            if fileid in documents:
                document = documents[fileid]
            else:
                continue
        else:
            document = Document.objects.filter(fileid=fileid)
            if document:
                document = document[0]
            else:
                continue
        sent,word_pos = get_sentence(fileid,position,term,src['sentence'])
        # sent = src['sentence']
        result.append({
            'document': document.id,
            # 'lemma_sentence': src['sentence'],
            'sentence':sent,
            'word_position':word_pos,
            'position': src['position']

        })
    return result

def filter_cat_era(term,era=None,category=None,lemma=True):
    es = connect_elasticsearch()
    index = get_sentence_index_name(lemma)
    query = {
        "size":0,
        'aggs':{
            't_matched':{
                "filter":{
                    "bool":{
                        "filter":[
                            {"term":{"sentence":term}}
                        ]
                    }
                },
                "aggs": {
                    "uni_eras":
                        {
                            "terms": {
                                "field": "era",
                            },
                            "aggs": {
                                "uni_cats":
                                    {
                                        "terms": {
                                            "field": "category",
                                        }
                                    }
                            }
                        }
                }
            }
        }
    }
    if era:
        if era in mapEraToEnglish:
            era = mapEraToEnglish[era]
        elif era not in mapEraToArabic:
            raise Exception('era does not exist')
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"era":era}})
    if category:
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"category":category}})
    r = es.search(index=index,body=query)
    eras = r['aggregations']['t_matched']['uni_eras']['buckets']

    result_couples = []
    print(eras)
    for era in eras:
        cats = era['uni_cats']['buckets']
        for cat in cats:
            result_couples.append((mapEraToArabic[era['key']], cat['key']))

    # hits = r['hits']['hits']
    # for hit in hits:
    #     print(hit['_source']['era'])
    return result_couples

def stats_words_appears(terms,era=None,category=None,lemma=True):
    es = connect_elasticsearch()
    index = get_sentence_index_name(lemma)
    query = {
        "size":0,
        'aggs':{
            't_matched':{
                "filter":{
                    "bool":{
                        "filter":[

                        ]
                    }
                },
                "aggs": {
                    "uni_eras":
                        {
                            "terms": {
                                "field": "era",
                            },
                            "aggs": {
                                "uni_cats":
                                    {
                                        "terms": {
                                            "field": "category",
                                        }
                                    }
                            }
                        }
                }
            }
        }
    }
    for term in terms:
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"sentence":term}})
    if era:
        if era in mapEraToEnglish:
            era = mapEraToEnglish[era]
        elif era not in mapEraToArabic:
            raise Exception('era does not exist')
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"era":era}})
    if category:
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"category":category}})
    r = es.search(index=index,body=query)
    eras = r['aggregations']['t_matched']['uni_eras']['buckets']

    result = {}
    print(eras)
    for era in eras:
        result[mapEraToArabic[era['key']]] = {}
        cats = era['uni_cats']['buckets']
        for cat in cats:
            result[mapEraToArabic[era['key']]][cat['key']] = cat['doc_count']

    return result



if __name__ == "__main__":
    result = filter_cat_era("من",category="شعر")
    print(result)
    filter_files_sents("من",page=2,perpage=3)