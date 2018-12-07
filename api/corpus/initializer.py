import os

from pathlib import Path
from .HistoricalCorpus import HistoricalCorpus
home = str(Path.home())
xmlDir = os.environ.get('XML_CORPUS_DIR', home + '/xmlCorpus') # where to put xml files
corpus = None
if os.path.isdir(xmlDir):
    corpus = HistoricalCorpus(xmlDir)

