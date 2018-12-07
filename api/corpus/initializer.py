try:
    from api.corpus import islamicbook_scrape
    from api.corpus import news_scrape
    from api.corpus import chi3r_scrape
    import api.corpus.cleaner as cleaner
except Exception:
    from . import islamicbook_scrape
    from . import news_scrape
    from . import chi3r_scrape
    from . import cleaner

import sys
import getopt
import os
from .HistoricalCorpus import HistoricalCorpus
from .basic import eras, path, xmlDir

def createDirectories():
    for x in eras:
        if not os.path.isdir(path + '/' + x):
            os.makedirs(path + '/' + x)  # line B
            print(x + ' created.')

def initialize(light_scrape = True):
    # try:
    #     from api.corpus import islamicbook_scrape
    #     from api.corpus import news_scrape
    #     from api.corpus import chi3r_scrape
    #     import api.corpus.cleaner as cleaner
    # except Exception:
    from . import islamicbook_scrape
    from . import news_scrape
    from . import chi3r_scrape
    from . import cleaner
    import os

    createDirectories()

    if light_scrape:
        # islamicbook_scrape.scrape_all(1)
        # news_scrape.scrape_all(1)
        chi3r_scrape.scrape_all(5)
    else:
        islamicbook_scrape.scrape_all()
        news_scrape.scrape_all()
        chi3r_scrape.scrape_all()

    # cleaning
    cleaner.clean()

    # convert to xml
    if not os.path.isdir(xmlDir):
        os.makedirs(xmlDir)  # line B
    cleaner.convertScrapedToXml(xmlDir)

if not os.path.isdir(xmlDir):
    print('Could not find corpus in', xmlDir)
    print('Scraping started')
    initialize()

corpus = HistoricalCorpus(xmlDir)

if __name__ == "__main__":
    initialize()
