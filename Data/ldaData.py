import os

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

os.chdir(baseGit+'/Data')
from analysisCrew import *

###Prepping all data
# years=[str(x) for x in range(1999,2014)]; sources=['StateHR','FH']
# years=[str(x) for x in range(2002,2013)]; sources=['StateHR','FH','FHpress','StateRF']
lFiles=filesToMerge(sources=['StateHR','FH'], years=range(1999,2014), window=True)
data=combineDicts(lFiles)

saveJSON(data, filename)