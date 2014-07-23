import os

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

os.chdir(baseGit+'/Data')
from ldaDataCrew import *

###Prepping all data
dataForLDA(
	filename='data_99-12_Shr-FH.json', 
	path=baseDrop+'/Data/forLDA', 
	yrs=range(1999,2013), 
	srcs=['StateHR','FH'], 
	roll=True, rsize=1)

dataForLDA(
	filename='data_02-13_All.json', 
	path=baseDrop+'/Data/forLDA', 
	yrs=range(2002,2013), 
	srcs=['StateHR','StateRF','FH','FHpress'], 
	roll=True, rsize=1)