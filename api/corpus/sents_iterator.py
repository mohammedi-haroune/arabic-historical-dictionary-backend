from itertools import islice
import nltk
try: from xml.etree import cElementTree as ElementTree
except ImportError: from xml.etree import ElementTree
from api.models import Document

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
    def __init__(self, corpus, fileid, size):
        self.tree_iterator = ElementTree.iterparse(corpus.abspath(fileid).open())
        self.num = 0
        self.size = size
        self.id = Document.objects.get(fileid=fileid).id

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.num < len(self):
            event, entry = self.tree_iterator.__next__()
            if entry.tag == "sentence" and entry.text is not None:
                n = {
                    'sentence': nltk.TreebankWordTokenizer().tokenize(entry.text),
                    'position': self.num,
                    'document': self.id
                }
                self.num = self.num + 1
                return n
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