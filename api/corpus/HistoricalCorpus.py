try: from xml.etree import cElementTree as ElementTree
except ImportError: from xml.etree import ElementTree

from nltk.corpus import XMLCorpusReader
import nltk
from nltk.internals import ElementWrapper
#import basic as bs

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
    def __init__(self, corpus, fileid):
        self.tree_iterator = ElementTree.iterparse(corpus.abspath(fileid).open())
        self.num = 0

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
        return 50

class HistoricalCorpus(XMLCorpusReader):


    def __init__(self, root, fileids=None, wrap_etree=False):
        if not fileids:
            fileids = '.*\.xml'
        super().__init__(root, fileids, wrap_etree)
        self._booksByEra = {}
        self._booksByType = {}
        for fileid in self.fileids():
            metadata = self.metadata(fileid)
            t = metadata['type']
            era = metadata['era']
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

    def _genSents(self,fileid,start=None,end=None):
        if not start:
            start = 0
        cpt = 0
        for event, entry in ElementTree.iterparse(self.abspath(fileid).open()):
            if entry.tag == "sentence" and entry.text is not None:
                print(entry.text)
                print(event)
                cpt += 1
                if end is not None and cpt > end:
                    break
                if cpt < start:
                    continue
                yield nltk.TreebankWordTokenizer().tokenize(entry.text)

    def _gen_sents_class_based(self, fileid):
        return SentsIterator(self, fileid)

    def sents(self,fileid,start=None,end=None):
        return [sent for sent in self._genSents(fileid,start,end)]

    def words(self, fileid=None,start=None,end=None):
        if not fileid:
            fileid = self.fileids()[0]
        if not start:
            start = 0
        sentences = self._genSents(fileid) #get all sentences generator
        words = []
        cpt = 0
        for sentence in sentences:
            if end is not None and cpt >= end:
                break
            print(cpt)
            print(len(sentence))
            if cpt < start:
                if cpt + len(sentence) >= start:
                    words += sentence[start-cpt:]
                cpt += len(sentence)
                continue
            words += sentence
            cpt += len(sentence)

        if end is not None and cpt > end:
            words = words[:-(cpt - end)]



        return words

    def sents_normalized(self, fileid,start=None,end=None):
        sentences = self.sents(fileid,start,end)
        return [[bs.normalizeText(word) for word in sentence] for sentence in sentences]

    def words_normalized(self, fileid=None,start=None,end=None):
        return [bs.normalizeText(word) for word in self.words(fileid,start,end)]



    def booksDescription(self):
        return [self.metadata(fileid) for fileid in self.fileids()]


    def metadata(self,fileid):
        info = {}
        encoding = self.encoding(fileid)
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
                break
        return info