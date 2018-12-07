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

from .basic import eras, path, xmlDir

def createDirectories():
    for x in eras:
        if not os.path.isdir(path + '/' + x):
            os.makedirs(path + '/' + x)  # line B
            print(x + ' created.')

def initialize():
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
    light_scrape = True

    options, remainder = getopt.getopt(sys.argv[1:], 'l', [])
    for opt, arg in options:
        if opt == '-l':
            print('light scraping mode selected')
            light_scrape = True
        else:
            print('heavy scrape mode selected')

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

if __name__ == "__main__":
    initialize()
