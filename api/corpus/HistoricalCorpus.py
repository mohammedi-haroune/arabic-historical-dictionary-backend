import os
import inspect

from pyarabic import araby

try: from xml.etree import cElementTree as ElementTree
except ImportError: from xml.etree import ElementTree

from itertools import islice

import nltk
from nltk.corpus import XMLCorpusReader
from nltk.internals import ElementWrapper

from .farassaWrapper.farassaInterface import Farasa


class Sliceable(object):
    """Sliceable(iterable) is an object that wraps 'iterable' and
    generates items from 'iterable' when subscripted. For example:

        >>> from itertools import count, cycle
        >>> s = Sliceable(count())
        >>> list(s[3:10:2])
        [3, 5, 7, 9]
        >>> list(s[3:6])
        [13, 14, 15]
        >>> next(Sliceable(cycle(range(7)))[11])
        4
        >>> s['string']
        Traceback (most recent call last):
            ...
        KeyError: 'Key must be non-negative integer or slice, not string'

    """
    def __init__(self, iterable):
        self.iterable = iterable

    def __getitem__(self, key):
        if isinstance(key, int) and key >= 0:
            return islice(self.iterable, key, key + 1)
        elif isinstance(key, slice):
            return islice(self.iterable, key.start, key.stop, key.step)
        else:
            raise KeyError("Key must be non-negative integer or slice, not {}"
                           .format(key))

class SentsIterator(object):
    def __init__(self, corpus, fileid,size):
        self.tree_iterator = ElementTree.iterparse(corpus.abspath(fileid).open())
        self.num = 0
        self.size = size

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.num < len(self):
            event, entry = self.tree_iterator.__next__()
            if entry.tag == "sentence" and entry.text is not None:
                return nltk.TreebankWordTokenizer().tokenize(entry.text)
            else:
                return self.next()
        else:
            raise StopIteration()

    def __getitem__(self, key):
        if isinstance(key, int) and key >= 0:
            return islice(self, key, key + 1)
        elif isinstance(key, slice):
            return islice(self, key.start, key.stop, key.step)
        else:
            raise KeyError("Key must be non-negative integer or slice, not {}"
                           .format(key))

    def __len__(self):
        return self.size

class HistoricalCorpus(XMLCorpusReader):


    def __init__(self, root, fileids=None, wrap_etree=False):
        if not fileids:
            fileids = '.*\.xml'
        super().__init__(root, fileids, wrap_etree)
        self._booksByEra = {}
        self._booksByType = {}
        self._eras = []
        self._categories = []
        self._fileidsByIds = {}
        self._idsByfileIds = {}
        self._far = None
        self.countFiles = 0
        for fileid in self.fileids():
            metadata = self.metadata(fileid)
            t = metadata['type']
            era = metadata['era']
            id = metadata['id']
            if era not in self._eras:
                self._eras.append(era)
            if t not in self._categories:
                self._categories.append(t)
            self._fileidsByIds[id] = fileid
            self._idsByfileIds[fileid] = id

            if era in self._booksByEra:
                self._booksByEra[era].append(fileid)
            else:
                self._booksByEra[era] = [fileid]
            if t in self._booksByType:
                self._booksByType[t].append(fileid)
            else:
                self._booksByType[t] = [fileid]


    def eras(self):
        return self._eras

    def categories(self):
        return self._categories

    def xml(self, fileid=None):
        # Make sure we have exactly one file -- no concatenating XML.
        if fileid is None and len(self._fileids) == 1:
            fileid = self._fileids[0]
        # Read the XML in using ElementTree.
        elt = ElementTree.parse(self.abspath(fileid).open()).getroot().find('doc')
        # If requested, wrap it.
        if self._wrap_etree:
            elt = ElementWrapper(elt)
        # Return the ElementTree element.
        return elt

    def fileids(self,era=None,category=None):
        if not era and not category:
            return super().fileids()
        fileids = []
        if era and era in self._booksByEra:
            fileids = self._booksByEra[era]
        if category and category in self._booksByType:
            if len(fileids):
                fileids = [fileid for fileid in self._booksByType[category] if fileid in fileids]
            else:
                fileids = self._booksByType[category]

        return fileids

    def _genSents(self,fileids=None,start=None,end=None,era=None,category=None):
        if not start:
            start = 0
        if era or category:
            fileids = self.fileids(era,category)
        if fileids is None:
            fileids = self.fileids()
        cpt = 0

        for fileid in fileids:
            for event, entry in ElementTree.iterparse(self.abspath(fileid).open()):
                if entry.tag == "sentence":
                    cpt += 1
                    if end is not None and cpt > end:
                        break
                    if cpt < start:
                        continue
                    try:
                        yield nltk.TreebankWordTokenizer().tokenize(entry.text)
                    except TypeError:
                        print(entry.text)
                        print(fileid)
                entry.clear()


    def _gen_sents_class_based(self, fileid):
        metadata = self.metadata(fileid)
        return SentsIterator(self, fileid,metadata["size"])

    def _genWords(self,fileids=None,start=None,end=None,era=None,category=None):
        sentences = self._genSents(fileids,era=era,category=category)
        if not start:
            start = 0
        limit = -1
        if end is not None:
            limit = end-start
        cpt = 0
        for sentence in sentences:
            if end is not None and cpt >= end:
                break
            print(cpt)
            print(len(sentence))
            words = []
            if cpt < start:
                if cpt + len(sentence) >= start:
                    words = sentence[start - cpt:]
                cpt += len(sentence)
            else:
                words = sentence
                cpt += len(sentence)
            for word in words:
                yield word
                limit -= 1
                if limit == 0:
                    break
            if limit == 0:
                break

    def sents(self,fileid=None,start=None,end=None,era=None,category=None):
        fileids = None
        if fileid is not None:
            fileids = [fileid]
        return [sent for sent in self._genSents(fileids,start,end,era,category)]

    def words(self, fileid=None,start=None,end=None,era=None,category=None):
        fileids = None
        if fileid:
            fileids = [fileid]
        words = [word for word in self._genWords(fileids,start,end,era=era,category=category)]
        return words

    def farasa(self):
        if not self._far:
            self._far = Farasa()
        return self._far
    def tagged_sents(self,fileid=None,start=None,end=None,era=None,category=None):
        sentences = self.sents(fileid,start,end,era,category)
        return [list(self.farasa().tag(" ".join(s))) for s in sentences]

    def tagged_words(self, fileid=None,start=None,end=None,era=None,category=None):
        words = self.words(fileid,start,end,era,category)
        return list(self.farasa().tag(" ".join(words)))

    def lemma_sents(self,fileid=None,start=None,end=None,era=None,category=None):
        sentences = self.sents(fileid,start,end,era,category)
        return [list(self.farasa().lemmatize(" ".join(s))) for s in sentences]

    def lemma_words(self, fileid=None,start=None,end=None,era=None,category=None):
        words = self.words(fileid,start,end,era,category)
        return list(self.farasa().lemmatize(" ".join(words)))

    def getIdFromFileid(self,fileid):
        return self._idsByfileIds[fileid]

    def getFileIdFromId(self,id):
        return self._fileidsByIds[id]

    def word_apparitions_gen(self,dictionarySet,fileid=None,era=None,
                          category=None,stop_words=None,get_sentences=False,context_size=5,
                             lemma=True, limit=-1, limitByFile=-1):
        if stop_words is None:
            root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            stop_words = root+'/stop_words'
            stop_words = open(stop_words,'r').readlines()
            stop_words = set(stop_word[:-1] for stop_word in stop_words)
        fileids = self.fileids(era, category)

        limits = dict((word, limit) for word in dictionarySet if word not in stop_words)
        if fileid:
            fileids = [fileid]
        for fileid in fileids:
            print('INFO GET APPEARS HISDICT: DOING FILE: ',fileid)
            self.countFiles += 1
            print('INFO GET APPEARS HISDICT: COUND FILES ',self.countFiles,
                  ' OUT OF ', len(self.fileids()))
            limitsbf = dict((word, limitByFile) for word in dictionarySet if word not in stop_words)
            id = self._idsByfileIds[fileid]
            sentences = self._genSents([fileid])
            i = 0
            for sentence in sentences:
                if lemma:
                    lsentence = self.farasa().lemmatize(" ".join(sentence))
                else:
                    lsentence = araby.strip_tashkeel(" ".join(sentence)).split()
                pos = 0
                for word in lsentence:
                    pos += 1

                    if word not in limitsbf:
                        continue
                    if word not in limits:
                        continue
                    if get_sentences:
                        low = max([0, pos - context_size])
                        high = min([len(sentence), pos + context_size])
                        out_sentence = sentence[low:high]
                        yield word, {"file_id": id, "sentence_pos": i,
                                     "word_pos": pos, 'sentence': " ".join(out_sentence)}
                    else:
                        yield word, {"file_id": id, "sentence_pos": i, "word_pos": pos}
                    limits[word] -= 1
                    if not limits[word]:
                        del limits[word]
                        if not len(limits):
                            return
                    limitsbf[word] -= 1
                    if not limitsbf[word]:
                        del limitsbf[word]
                i += 1


    def words_apparitions(self,dictionarySet,fileid=None,era=None,
                          category=None,stop_words=None,get_sentences=False,context_size=5,
                          lemma=True,limit=-1,limitByFile=-1):
        apparitions = {}
        eras = self.eras()
        categories = self.categories()
        if era:
            eras = [era]
        if category:
            categories = [category]
        self.countFiles = 0
        for era in eras:
            for category in categories:
                for w, info in self.word_apparitions_gen(dictionarySet, fileid, era, category,
                                                         stop_words, get_sentences, context_size,
                                                         lemma, limit,limitByFile):
                    if w in apparitions:
                        apparitions[w].append(info)
                    else:
                        apparitions[w] = [info]
        apparitions = dict((w,apparitions[w]) for w in apparitions if len(apparitions[w]))
        return apparitions


    def booksDescription(self):
        return [self.metadata(fileid) for fileid in self.fileids()]


    def metadata(self,fileid):
        info = {}
        for event, entry in ElementTree.iterparse(self.abspath(fileid).open()):
            if entry.tag == "metadata":
                info['book_name'] = entry.find('book_name').text
                info['type'] = entry.find('type').text
                info['author'] = {}
                author = entry.find('author')
                info['author']['name'] = author.find('name').text
                info['author']['birth'] = author.find('birth').text
                info['author']['death'] = author.find('death').text
                info['era'] = entry.find('era').text
                info['fileid'] = fileid
                info['id'] = int(entry.find('id').text)
                info['size'] = int(entry.find('size').text)
                break
        return info