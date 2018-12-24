from elasticsearch.helpers import bulk

from api.corpus.initializer import corpus
from api.corpus.search.common import connect_elasticsearch, get_sentence_index_name


def create_sentence_index(index,es):
    mapping = {
        "mappings": {
            "sent": {
                "properties": {
                    "parent":{"type":"keyword"},
                    "sentence":{"type":"text"},
                    "position":{"type":"integer"},
                    'book': {"type":"text", "fielddata":True},
                    'era': {"type":"keyword"},
                    'category': {"type":"keyword"}
                }
            }
        }
    }
    es.indices.create(index=index,body=mapping)

def split_sentences(fileids,batch=1000000,lemma=True):
    result = []
    wcount = 0
    for fileid in fileids:
        print('INFO ELASTIC ADD: DOING FILE',fileid)
        if lemma:
            sentences = corpus.gen_lemma_sents(fileid=fileid)
        else:
            sentences = corpus.gen_sents(fileids=[fileid])
        meta = corpus.metadata(fileid)
        for i,s in enumerate(sentences):
            result.append({
                'parent': fileid,
                'sentence': s,
                'position': i,
                'book': meta['book_name'],
                'era': meta['era'],
                'category': meta['type']
            })
            wcount += len(s)
            if wcount >= batch:
                print('INFO ELASTIC: WORD COUNT IS ',wcount)
                yield result
                wcount = 0
                result = []

    if len(result):
        yield result


def add_all_docs(lemma=True):
    es = connect_elasticsearch()
    if not es:
        print("ERROR ELASTIC FILL: COULDN'T CONNECT")
        return False
    result = split_sentences(corpus.fileids(),lemma=lemma)
    index = get_sentence_index_name(lemma)
    create_sentence_index(index,es)
    for sentences in result:
        sentences = [{"_index": index,
                      "_type": "sent",
                      "_source": sentence
                      } for sentence in sentences]
        r = bulk(es, sentences)
        print('INFO ELASTIC ADD: BULK CREATED!')
        print(r)
    return True


if __name__ == '__main__':
    add_all_docs(True)
