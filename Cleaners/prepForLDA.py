import os
baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif/'

os.chdir(baseGit+'Cleaners')
from cleanCrew import *

# FH (98-14), FHpress (02-13), StateHR (99-13), StateRF (01-12)
files=[{'name':'FH','years':range(1998,2000)},
		{'name':'FH','years':range(2001,2015)},
		{'name':'FHpress','years':range(2002,2014)},
		{'name':'StateHR','years':range(1999,2014)},
		{'name':'StateRF','years':range(2001,2013)}]

toClean=ListOfFiles(files)
toClean.append('StateRF_2010_5.json')

# Clean each file
for file in toClean:
	prepForLDA(file, 
		baseDrop+'Data/Raw',
		baseDrop+'Data/forLDA')