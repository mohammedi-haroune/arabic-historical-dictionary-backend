import xml.etree.cElementTree as ET
import basic as bs
from HistoricalCorpus import HistoricalCorpus
import os

def clean():
    _cleanNotFound()
    _moveAstrayBooks([])

def _cleanNotFound():
    bookByEras = bs.loadListOfBooksByEras()
    for era in bookByEras:
        books = bookByEras[era]
        for book in books:
            notFound = False
            with open(book['path'],'r') as f:
                empty = True
                for line in f:
                    if len(line) > 0:
                        empty = False
                    if 'sorry' in line.lower():
                        print(line)
                        notFound = True
            if notFound or empty:
                os.remove(book['path'])

def _moveAstrayBooks(booksToMove):
    pass

def _createXml(path,name,author,type,savePath,era):
    root = ET.Element("root",encoding='utf-8')
    metaData = ET.SubElement(root,'metadata')
    ET.SubElement(metaData, 'book_name').text = name
    ET.SubElement(metaData, 'era').text = era
    auth = ET.SubElement(metaData, 'author')
    ET.SubElement(auth, 'name').text = author['name']
    ET.SubElement(auth, 'birth').text = str(author['birth'])
    ET.SubElement(auth, 'death').text = str(author['death'])
    ET.SubElement(metaData, 'type').text = type
    doc = ET.SubElement(root, "doc")
    content = open(path,'r').read()
    sentences = _sentenceTokenizer(content)
    for sentence in sentences:
        ET.SubElement(doc, "sentence").text = sentence
    tree = ET.ElementTree(root)
    filepath = savePath+'/'+name+".xml"
    tree.write(filepath)
    return filepath

def _sentenceTokenizer(content):
    sentences = content.splitlines()#re.findall('([^:]+?\.|[^:]+?\.\.\.|[^:]+?؟|[^:]+?!|[^:]+?:)', content,flags=re.MULTILINE)
    return sentences
def convertScrapedToXml(xmlDir='xmlCorpus'):
    books = bs.loadListOfBooksByEras()
    import json

    # bk = {}

    for era in bs.eras:
        dir = xmlDir + '/' + era
        # bk[era] = {}
        if not os.path.isdir(dir):
            os.mkdir(dir)
        limit = -1
        for book in books[era]:
            print(book)
            try:
                infos = bs.getBirthDeathFromAuthor(book['author'])
            except Exception:
                continue
            author = {'name': book['author'], 'birth': infos[0], 'death': infos[1]}
            path = _createXml(book['path'], book['name'], author, book['type'], dir,era)
            # if book['type'] in bk[era]:
            #     bk[era][book['type']].append(book)
            # else:
            #     bk[era][book['type']] = [book]
            limit-=1
            if not limit: break
    corpus = HistoricalCorpus(xmlDir)
    bk = corpus.booksDescription()
    with open(xmlDir+'/books_description.json', 'w') as fp:
        json.dump(bk, fp)
def _readXml():
    import nltk
    corpus = HistoricalCorpus('xmlCorpus','.*\.xml')
    print(len(corpus.fileids()))
    # print(corpus.sents(corpus.fileids()[1]))
    # corpus.metadata(corpus.fileids()[0])
    print(corpus.fileids(bs.eras[2]))
    print(corpus.fileids(category="religion"))
    print(corpus.fileids(bs.eras[2],'religion'))


if __name__ == '__main__':
    convertScrapedToXml()
# readXml()