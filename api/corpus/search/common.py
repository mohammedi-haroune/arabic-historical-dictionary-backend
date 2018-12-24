from elasticsearch import Elasticsearch



def connect_elasticsearch():
    port = 9200
    ip_address = '35.226.252.137'
    _es = Elasticsearch([{'host': ip_address , 'port': port}], timeout=30)
    if _es.ping():
        print('INFO ELASTIC: CONNECTED')
    else:
        print('INFO ELASTIC: COULD NOT CONNECT')

    return _es

def get_sentence_index_name(lemma):
    if lemma:
        index = 'lemma_sentences'
    else:
        index = 'sentences'
    return index