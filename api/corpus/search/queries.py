from django.http import JsonResponse

from api.corpus.search.common import connect_elasticsearch, get_sentence_index_name


def filter_files_sents(term,era=None,category=None,fileid=None,page=1,perpage=20,lemma=True):
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
        query['query']['bool']['filter'].append({"term":{"era":era}})
    if category:
        query['query']['bool']['filter'].append({"term":{"category":category}})
    if fileid:
        query['query']['bool']['filter'].append({"term":{"parent":fileid}})
    r = es.search(index=index,body=query)
    r = r['hits']['hits']
    result = []
    for res in r:
        src = res['_source']
        result.append({
            'fileid': src['parent'],
            'book': src['book'],
            'sentence': src['sentence'],
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
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"era":era}})
    if category:
        query['aggs']['t_matched']['filter']['bool']['filter'].append({"term":{"category":category}})
    r = es.search(index=index,body=query)
    eras = r['aggregations']['t_matched']['uni_eras']['buckets']
    result = {'eras': [], 'categories': []}

    for era in eras:
        result['eras'].append(era['key'])
        cats = era['uni_cats']['buckets']
        for cat in cats:
            result['categories'].append(cat['key'])
    result['eras'] = list(set(result['eras']))
    result['categories'] = list(set(result['categories']))
    # hits = r['hits']['hits']
    # for hit in hits:
    #     print(hit['_source']['era'])
    return result


if __name__ == "__main__":
    result = filter_cat_era("من",category="شعر")
    print(result)
    filter_files_sents("من",page=2,perpage=3)