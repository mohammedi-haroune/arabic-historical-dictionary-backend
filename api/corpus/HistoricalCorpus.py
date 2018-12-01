try: from xml.etree import cElementTree as ElementTree
except ImportError: from xml.etree import ElementTree

from nltk.corpus import XMLCorpusReader
import nltk
from nltk.internals import ElementWrapper


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

    def sents(self,fileid):
        doc = self.xml(fileid)
        encoding = self.encoding(fileid)
        iterator = doc.getiterator()
        out = []

        for node in iterator:
            text = node.text
            if text is not None:
                if isinstance(text, bytes):
                    text = text.decode(encoding)
                out.append(nltk.wordpunct_tokenize(text))
        return out

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