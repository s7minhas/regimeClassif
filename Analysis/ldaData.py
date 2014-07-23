# helpful packages
import os
import string
from countrycode import countrycode
from compiler.ast import flatten
from difflib import get_close_matches
import json
import csv
from gensim import corpora, models, similarities
from operator import itemgetter

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

os.chdir(baseGit+'/Analysis')
from analysisCrew import *

###Prepping all data
# years=[str(x) for x in range(1999,2014)]; sources=['StateHR','FH']
# years=[str(x) for x in range(2002,2013)]; sources=['StateHR','FH','FHpress','StateRF']
lFiles=filesToMerge(sources=['StateHR','FH'], years=range(1999,2014), window=True)
data=combineDicts(lFiles)