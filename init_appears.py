from api.corpus.initializer import corpus
import os



fileids = corpus.fileids()
sizedFiles = [fileid for fileid in fileids if os.path.getsize(corpus.abspath(fileid)) > 100000000]
print(sizedFiles)

from api.corpus.search.fill_indices import split_sentences
from elasticsearch.helpers import bulk
from api.corpus.search.common import connect_elasticsearch, get_sentence_index_name
fileid = 'xmlCorpus/Abbasid/التفاسير/تفسير الطبري = جامع البيان ت شاكر.xml'
es = connect_elasticsearch()
result = split_sentences([fileid])
index = get_sentence_index_name(True)
for sentences in result:
    sentences = [{"_index": index,
                  "_type": "sent",
                  "_source": sentence
                  } for sentence in sentences]
    r = bulk(es, sentences)
    print('INFO ELASTIC ADD: BULK CREATED!')
    print(r)

# xmlCorpus/Abbasid/التفاسير/تفسير الطبري = جامع البيان ت شاكر.xml
# xmlCorpus/Modern/أخبار/Collection-arabic.cnn.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-news.bbc.co.uk.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-thawra.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.ahram.org.eg.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.akhbar-libya.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.al-watan.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.almshaheer.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.alquds.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.alwatan.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.aps.dz.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.asharqalawsat.com.list.txt.xml
# xmlCorpus/Modern/أخبار/Collection-www.attajdid.ma.list.txt.xml


# xmlCorpus/Modern/أخبار/Collection-arabic.cnn.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-news.bbc.co.uk.list.txt.xml xmlCorpus/Modern/أخبار/Collection-thawra.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.ahram.org.eg.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.akhbar-libya.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.al-watan.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.almshaheer.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.alquds.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.alwatan.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.aps.dz.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.asharqalawsat.com.list.txt.xml xmlCorpus/Modern/أخبار/Collection-www.attajdid.ma.list.txt.xml