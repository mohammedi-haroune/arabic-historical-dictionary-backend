import urllib.request
from bs4 import BeautifulSoup
import basic as bs
import re

""" procedure :
website -> jahili -> {
                          cha3ir1 -> diwan -> {
                                              chi3r1 ,
                                              chi3r2 ,
                                              ....
                                              },
                          cha3ir2 -> diwan -> {
                                              chi3r1 ,
                                              chi3r2 ,
                                              ...
                                              }
                          ...
                          } """


def scrape_all(limit = -1):
    rep = urllib.request.urlopen("https://www.aldiwan.net/")
    soup = BeautifulSoup(rep, "lxml")
    i = 0
    mapEras = {
        "العصر الجاهلي" : bs.eras[0],
        'عصر المخضرمون': bs.eras[1],
        "العصر الإسلامي" : bs.eras[1],
        "العصر الاموي" : bs.eras[2],
        "العصر العباسي" : bs.eras[3],
        'العصر الايوبي' : bs.eras[4],
        'العصر العثماني' : bs.eras[4],
        'العصر المملوكي' : bs.eras[4],
        'العصر الأندلسي' : bs.eras[4],
        'العصر الحديث' : bs.eras[5]
    }

    books = bs.loadListOfBooksByEras()
    exceptions = open("exceptions.txt", encoding="utf-8", mode="w")
    for eras in soup.find_all("div", {"class": "col-md-4"}):
        for node in eras.find_all("a"):
            if node.text in mapEras:# ["العصر الجاهلي", "العصر العباسي", "العصر الإسلامي",
                             #"العصر الاموي"]:  # get all jahili cho3araa list link
                setLimit = limit
                rep = urllib.request.urlopen("https://www.aldiwan.net/" + node.get("href"))
                soup = BeautifulSoup(rep, "lxml")

                for node1 in soup.find_all("a", {"class": "s-button"}):  # get every cha3ir diwan
                    rep = urllib.request.urlopen("https://www.aldiwan.net/" + node1.get("href"))
                    soup2 = BeautifulSoup(rep, "lxml")

                    for node3 in soup2.find_all("a", {"class": "pull-right"}):  # get every chi3r from diwan link
                        #   create a file for everykassida using getFilePath function


                        print("try")
                        print(i)
                        i = i + 1
                        cEra = mapEras[node.text]
                        if not cEra:
                            print(node.text)
                            continue
                        if bs.bookExists(node3.text,books):
                            setLimit -= 1
                            if not setLimit:
                                break
                            continue
                        filename = bs.getFilePath(node3.text, cEra, "poem", node1.text)

                        # if node.text == "العصر الجاهلي":
                        #     filename = bs.getFilePath(node3.text, "Jahiliy", "poem", node1.text) + ".txt"
                        #     # error in line 40 in one of the files i get file not found (file not getting created)
                        # elif node.text == "العصر العباسي":
                        #     filename = bs.getFilePath(node3.text, "Abbasid", "poem", node1.text) + ".txt"
                        # elif node.text == "العصر الأموي":
                        #     filename = bs.getFilePath(node3.text, "Umayyad", "poem", node1.text) + ".txt"
                        # elif node.text == "العصر الإسلامي":
                        #     filename = bs.getFilePath(node3.text, "SadrIslam", "poem", node1.text) + ".txt"
                        print('got name')
                        try:
                            file = open(filename, encoding="utf-8", mode="w")
                            print("file created")
                            print(filename)
                            rep = urllib.request.urlopen("https://www.aldiwan.net/" + node3.get("href"))
                            soup3 = BeautifulSoup(rep, "lxml")
                            for main_text in soup3.find_all("div", {"class": "bet-1"}):  # access to kassida link and
                                chatr = 1
                                for prt in main_text.find_all("h3"):
                                    if chatr % 2 == 0:
                                        file.write(prt.text)
                                    else:
                                        file.write(re.sub("\n", "\t", prt.text))
                                    chatr = chatr + 1
                                break
                            file.close()
                            setLimit -= 1
                            if not setLimit:
                                break
                            print("file close")
                        except IOError:
                            print("inside exception")
                            exceptions.write(filename)
                        if not setLimit:
                            break
                    if not setLimit:
                        break

if __name__ == '__main__':
    scrape_all()
