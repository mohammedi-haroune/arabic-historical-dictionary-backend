
from initializer import eras, eraEnd, eraStart, path
import pyarabic.araby as ar

def normalizeText(content):
    content = ar.strip_tatweel(content)
    content = ar.strip_tashkeel(content)
    content = ar.normalize_ligature(content)
    return content

def getFilePath(name,era,type='divers',author="unknown"):
    import os
    if era not in eras:
        return None #come on ..
    name = normalizeText(name)
    author = normalizeText(author)
    if not os.path.isdir(path + '/' + era + '/' + type):
        os.mkdir(path + '/' + era + '/' + type)
    if author != "":
        name = "__"+author+"__"+name
    p = path + '/' + era + '/' + type + '/' + name
    p = p.replace('\t', ' ')
    p = p.replace('\n', ' ')
    p = p.replace('\r', ' ')
    return p

def getErasDict():
    return dict([(era,(start,end)) for era,start,end in zip(eras,eraStart,eraEnd)])

def getEraFromDate(date):
    for i,(start,end) in enumerate(zip(eraStart,eraEnd)):
        if start <= date < end:
            return eras[i]
    return None

def getBirthDeathFromAuthor(name,lang='ar'):
    import wptools as wp
    import re
    patternsDeath = [
        ".*Décès en.*?(\d+)",
        "^.*وفيات (\d+)$",
        ".*?(\d+) deaths",
    ]
    patternsBirth = [
        ".*Naissance en.*?(\d+)",
        ".*?(\d+) births",
        "^.*مواليد (\d+)$"
    ]
    try:
        so = wp.page(name, lang=lang).get_more()
        infos = []
        print(so.data['categories'])
        for st in so.data['categories']:
            done = False
            for pattern in patternsBirth:
                if re.match(pattern, st):
                    date = int(re.sub(pattern, "\g<1>", st))
                    # print(st)
                    print(date)
                    infos.append(date)
                    done = True
                    break
            if done: break
        if len(infos) == 0:
            infos.append("unknown")
        for st in so.data['categories']:
            done = False
            for pattern in patternsDeath:
                if re.match(pattern, st):
                    date = int(re.sub(pattern, "\g<1>", st))
                    # print(st)
                    print(date)
                    infos.append(date)
                    done=True
                    break
            if done: break
        if len(infos) == 1:
            infos.append('unknown')

        return infos
    except Exception:
        res = wikipediaFromGoogle(name)
        if res:
            lang = res[0]
            name = res[1]
        else:
            return ["unknown","unknown"]
        try:
            so = wp.page(name, lang=lang).get_more()
            infos = []
            print(so.data['categories'])
            for st in so.data['categories']:
                done = False
                for pattern in patternsBirth:
                    if re.match(pattern, st):
                        date = int(re.sub(pattern, "\g<1>", st))
                        # print(st)
                        print(date)
                        infos.append(date)
                        done = True
                        break
                if done: break
            if len(infos) == 0:
                infos.append("unknown")
            for st in so.data['categories']:
                done = False
                for pattern in patternsDeath:
                    if re.match(pattern, st):
                        date = int(re.sub(pattern, "\g<1>", st))
                        # print(st)
                        print(date)
                        infos.append(date)
                        done = True
                        break
                if done: break
            if len(infos) == 1:
                infos.append('unknown')
            return infos

        except Exception:
            return ["unknown","unknown"]

def getEraFromAuthor(name,lang='ar'):
    death = getBirthDeathFromAuthor(name,lang)[1]
    if death != 'unknown':
        return getEraFromDate(death)
    birth = getBirthDeathFromAuthor(name, lang)[0]
    if birth != 'unknown':
        return getEraFromDate(birth)
    return 'unknown'

def wikipediaFromGoogle(query):
    import re
    from bs4 import BeautifulSoup
    import requests
    query = re.sub("\s","+",query)
    link = "https://www.google.com/search?sclient=psy-ab&client=ubuntu&hs=k5b&channel=fs&biw=1366&bih=648&noj=1&q="+query
    # r = requests.get(link)
    rep = requests.get(link)
    soup = BeautifulSoup(rep.text,"html.parser")
    cite = soup.find("cite")
    if cite:
        first = cite.get_text()
    else:
        return None
    result = None
    if re.match("https://.+\.wikipedia.org/wiki/.+",first):
        result = re.sub("https://(.+)\.wikipedia.org/wiki/(.+)","\g<1>*\g<2>",first).split("*")
    if not result:
        return None
    return str(result[0]),re.sub("_"," ",result[1])


def saveListOfBooks():
    import json
    books = loadListOfBooksByEras()
    with open('books.json', 'w') as fp:
        json.dump(books, fp)

def bookExists(name,allBooks=None):
    name = normalizeText(name)
    if not allBooks:
        allBooks = loadListOfBooksByEras()
    for era in eras:
        books = allBooks[era]
        for book in books:
            if name == book['name']:
                return True
    return False

def loadListOfBooksByEras():
    import re
    import os
    books = {}
    for rootdir in eras:
        books[rootdir] = []
        for folder, subs, files in os.walk(path+'/'+rootdir):
            if len(files):
                # print(files)
                splitted = [re.findall("__(.*)__(.*)", file)[0] for file in files]
                # print(splitted)
                category = folder.split('/')[-1]
                books[rootdir] += [{"name": spl[1], "author": spl[0],
                                   "type": category, "path":folder+'/'+file}
                                  for spl,file in zip(splitted,files)]
    # print(books)
    return books





if __name__ == "__main__":
    # saveListOfBooks()
    print(getEraFromAuthor("إبراهيم بن محمد الحقي","ar"))
    # res = wikipediaFromGoogle("ghandi")
    # if res:
    #     print(res[0])
    #     print(res[1])
    #     print(getEraFromAuthor(res[1],res[0]))
