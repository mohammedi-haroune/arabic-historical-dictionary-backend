import urllib.request
from bs4 import BeautifulSoup
import basic as bs

def scrape_all(limit=-1):
  rep = urllib.request.urlopen("http://aracorpus.e3rab.com/argistestsrv.nmsu.edu/AraCorpus/Data/")
  soup = BeautifulSoup(rep, "html.parser")
  names = []
  books = bs.loadListOfBooksByEras()
  for node in soup.find_all("a"):
    if node.get("href").endswith("txt"):
      # Asr hadith, category => news
      if bs.bookExists(node.text,bs.eras[-1],books):
          continue
      fileName = bs.getFilePath(node.text, bs.eras[-1], "news")

      file = open(fileName, encoding="utf-8", mode="w")
      file.write(urllib.request.urlopen(
        "http://aracorpus.e3rab.com/argistestsrv.nmsu.edu/AraCorpus/Data/" + node.text).read().decode('windows-1256'))
      print("the file : " + node.text + "is writen succesfully")
      limit -= 1
      if not limit:
        break

if __name__ == '__main__':
    scrape_all()