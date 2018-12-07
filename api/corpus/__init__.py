from .HistoricalCorpus import HistoricalCorpus
from .initializer import initialize
from .basic import xmlDir
import os

if not os.path.isdir(xmlDir):
    print('Could not find corpus in', xmlDir)
    print('Scraping started')
    initialize()

corpus = HistoricalCorpus(xmlDir)
