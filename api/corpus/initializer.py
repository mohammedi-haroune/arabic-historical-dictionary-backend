import sys
import getopt
from pathlib import Path
home = str(Path.home())
import tempfile

eras = ['Jahiliy','SadrIslam','Umayyad','Abbasid','Dual','Modern']
mapEraToArabic = {
    eras[0]: 'العصر الجاهلي',
    eras[1]: 'عصر صدر الإسلام',
    eras[2]: 'عصر بني أمية',
    eras[3]: 'عصر بني العباس',
    eras[4]: 'عصر الدول المتتابعة',
    eras[5]: 'العصر الحديث'
}
eraStart = [460,610,661,750,1258,1798]
eraEnd = [610,661,750,1258,1798,2019]
path = tempfile.gettempdir()+"/rawData" # where to put scraped files
xmlDir = str(Path.home())+'/xmlCorpus'  # where to put xml files
def createDirectories():
    import os
    for x in eras:
        if not os.path.isdir(path + '/' + x):
            os.makedirs(path + '/' + x)  # line B
            print(x + ' created.')

if __name__ == "__main__":
    import islamicbook_scrape
    import news_scrape
    import chi3r_scrape
    import cleaner
    import os

    createDirectories()
    light_scrape = True

    options, remainder = getopt.getopt(sys.argv[1:], 'l',[])
    for opt,arg in options:
        if opt == '-l':
            print('light scraping mode selected')
            light_scrape = True
        else:
            print('heavy scrape mode selected')


    if light_scrape:
        islamicbook_scrape.scrape_all(3)
        # news_scrape.scrape_all(1)
        chi3r_scrape.scrape_all(20)
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