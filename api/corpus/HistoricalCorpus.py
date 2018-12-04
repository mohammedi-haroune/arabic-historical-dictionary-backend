try: from xml.etree import cElementTree as ElementTree
except ImportError: from xml.etree import ElementTree

from nltk.corpus import XMLCorpusReader
import nltk
from nltk.internals import ElementWrapper
import basic as bs
from itertools import islice

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
        self._fileidsByIds = {}
        self._idsByfileIds = {}
        for fileid in self.fileids():
            metadata = self.metadata(fileid)
            t = metadata['type']
            era = metadata['era']
            id = metadata['id']

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
                    yield nltk.TreebankWordTokenizer().tokenize(entry.text)

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

    def sents_normalized(self, fileid,start=None,end=None,era=None,category=None):
        sentences = self.sents(fileid,start,end,era,category)
        return [[bs.normalizeText(word) for word in sentence] for sentence in sentences]

    def words_normalized(self, fileid=None,start=None,end=None,era=None,category=None):
        return [bs.normalizeText(word) for word in self.words(fileid,start,end,era,category)]

    def getIdFromFileid(self,fileid):
        return self._idsByfileIds[fileid]

    def getFileIdFromId(self,id):
        return self._fileidsByIds[id]

    def words_apparitions(self,fileid=None,era=None,category=None,stop_words=None):
        fileids = self.fileids(era,category)
        if fileid:
            fileids = [fileid]
        apparitions = {}
        for fileid in fileids:
            id = self._idsByfileIds[fileid]
            sentences = self._genSents([fileid])
            for i,sentence in enumerate(sentences):
                for word in sentence:
                    if stop_words and word in stop_words:
                        continue

                    if word not in apparitions:
                        apparitions[word] = [(id,i)]
                    else:
                        apparitions[word].append((id,i))
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