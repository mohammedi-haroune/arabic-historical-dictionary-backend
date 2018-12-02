import xml.etree.cElementTree as ET
import basic as bs
import initializer
from HistoricalCorpus import HistoricalCorpus
import os
import nltk

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
def _normalize_text(content):
    import pyarabic.araby as ar
    content = ar.strip_tatweel(content)
    content = ar.strip_tashkeel(content)
    content = ar.normalize_ligature(content)
    return content

def _clean_text(content):
    content = _normalize_text(content)
    return content

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
    content = _clean_text(content)
    sentences = _sentenceTokenizer(content)
    for sentence in sentences:
        ET.SubElement(doc, "sentence").text = sentence
    tree = ET.ElementTree(root)
    savePath = savePath+'/'+type
    if not os.path.isdir(savePath):
        os.mkdir(savePath)
    filepath = savePath+'/'+name+".xml"
    tree.write(filepath)
    return filepath

def containsPunctuation(content):
    if '.' in content:
        return True
    return False
def _sentenceTokenizer(content):
    if not containsPunctuation(content):
        return content.splitlines() #if it doesn't contains punctuation we split by line
    sentences = nltk.PunktSentenceTokenizer().tokenize(content)
    return sentences

def convertScrapedToXml(xmlDir='xmlCorpus'):
    books = bs.loadListOfBooksByEras()
    import json

    tempAuthors = {}
    for era in bs.eras:
        dir = xmlDir + '/' + era
        if not os.path.isdir(dir):
            os.mkdir(dir)
        limit = -1
        for book in books[era]:
            print(book)
            if book['author'] in tempAuthors:
                infos = tempAuthors[book['author']]
            else:
                try:
                    infos = bs.getBirthDeathFromAuthor(book['author'])
                    tempAuthors[book['author']] = infos
                except Exception:
                    continue

            author = {'name': book['author'], 'birth': infos[0], 'death': infos[1]}
            path = _createXml(book['path'], book['name'], author, book['type'], dir,era)
            limit-=1
            if not limit: break
    corpus = HistoricalCorpus(xmlDir)
    bk = corpus.booksDescription()
    with open(xmlDir+'/books_description.json', 'w') as fp:
        json.dump(bk, fp)
def _readXml():
    corpus = HistoricalCorpus(initializer.xmlDir)
    print(len(corpus.fileids()))
    # print(corpus.sents(corpus.fileids()[1]))
    # corpus.metadata(corpus.fileids()[0])
    print(corpus.fileids(bs.eras[2]))
    print(corpus.fileids(category="poem"))
    file = corpus.fileids(category="history",era='Abbasid')[0]
    print(file)
    words = corpus.words(file,30,60)
    print(words)
    print(len(words))


if __name__ == '__main__':
    # convertScrapedToXml()
    print(_normalize_text('yasserُ'))
    print('done')
    _normalize_text('أَرَسمــاً جَديداً مِن نَوارَ تَعَرُّفُ العصر الاموي')
    words = nltk.TreebankWordTokenizer().tokenize('أَرَسمــاً جَديداً مِن نَوارَ تَعَرُّفُ العصر الاموي')
    print(words)
    _readXml()