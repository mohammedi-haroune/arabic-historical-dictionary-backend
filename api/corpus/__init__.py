from .HistoricalCorpus import HistoricalCorpus
from pathlib import Path
from .initializer import init, xmlDir, eras, mapEraToArabic
import os

if not os.path.isdir(xmlDir):
    print('Could not find corpus in', xmlDir)
    print('Scraping started')
    init()

corpus = HistoricalCorpus(xmlDir)
