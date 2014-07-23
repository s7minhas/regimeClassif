import os
import string
from countrycode import countrycode
from compiler.ast import flatten
from difflib import get_close_matches
import json
import csv

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

def dataForLDA(filename, path, yrs, srcs, roll, rsize):
	"""Aggregate function to prepare then save data"""
	print 'Start data combo of: ' + ' and '.join(srcs) + \
	' from ' + str(yrs[0]) + ' to ' + str(yrs[len(yrs)-1]) + '\n'
	lFiles=filesToMerge(sources=srcs, years=yrs, 
		window=roll, wdow=rsize)
	data=combineDicts(lFiles)
	os.chdir(path)
	saveJSON(data, filename)
	print 'Data combo complete for: ' + ' and '.join(srcs) + \
	' from ' + str(yrs[0]) + ' to ' + str(yrs[len(yrs)-1]) + '\n'

def fhYrFix(x):
	"""Fix for FH year labels in filename"""
	src=x.split('_')[0]
	yr=x.split('_')[1]
	if src[0:2]=='FH' and int(yr)>1999:
		return str( int(yr)-1  )
	else:
		return yr

def wdowYr(yr, wdow):
	"""Helper for creating moving window"""
	wYrs=[str(int(yr)-x) for x in range(0,wdow+1)]
	return [x for x in wYrs if int(x)>1998]

def filesToMerge(sources, years, window=False, wdow=2):
	"""Pull out list of filenames for a
	 particular time period"""	
	years=[str(x) for x in years]
	filesSrc=[f for f in os.listdir(baseDrop+'/Data/forLDA') 
		if f.split('_')[0] in sources]
	if window:
		toMerge=[[f for f in filesSrc if fhYrFix(f) 
			in wdowYr(year, wdow)] for year in years]
	else: 
		toMerge=[[f for f in filesSrc if fhYrFix(f) in year]
			for year in years]
	for x in toMerge:
		print '\t\tMerging: ' + ' and '.join(x) + '\n'
	return toMerge

def loadJSON(file):
	"""Load json files"""
	return json.load(open(baseDrop+'/Data/forLDA/'+file, 'rb'))

def dictPull(dataDict, key):
	"""Pull out a list of values from a 
	dictioanry based on key"""
	info=[]
	for dat in dataDict:
		if not isinstance(dat[key], list):
			if dat[key]==u'C\xc3\xb4te d&#039;Ivoire' or dat[key]==u'C\xf4te d&#039;Ivoire':
				info.append('Ivory Coast')
			elif dat[key]==u'S\xe3o Tom\xe9 and Pr\xedncipe':
				info.append('Sao Tome and Principe')
			else:
				info.append(dat[key].encode('utf-8'))
		else:
			tmp=[x.encode('utf-8') for x in dat[key]]
			info.append(tmp)
	return info

def closeMatchI(string, words):
	"""Find closest match to string in list"""
	val=get_close_matches(string, words, n=1, cutoff=0.3)
	return words.index(val[0])

def cname(data, details=False):
	"""Standardize country names"""
	cntrs=dictPull(data, 'name')
	cntrs[closeMatchI('Congo Democratic of',cntrs)]='Congo, Democratic'
	cntrs[closeMatchI('Congo Republic of',cntrs)]='Congo, Republic'
	cntrsClean=countrycode(cntrs,'country_name','country_name')
	for ii in range(0,len(cntrsClean)):
		data[ii]['nameClean']=cntrsClean[ii].lower()
		if(details):
			print data[ii]['name'] + ' ---> ' + cntrsClean[ii] + '\n'
	return data

def getCntries(add=[]):
	"""Pulls up a list of countries for analysis"""
	d=open(baseDrop+'/Data/Components/cntriesForAnalysis.csv', 'rU')
	reader=csv.reader(d, dialect=csv.excel_tab)
	cntries=[x.lower() for x in flatten([x for x in reader])]
	if len(add)!=0:
		cntries.extend(add.lower())
	return cntries	

def subsetDictByCntry(data, cntries=getCntries(), details=False):
	"""Remove countries that are not in the 
	getCntries list, this gets rid of units like
	Palestinian territories"""
	ndata=[]
	for dat in data:
		if dat['nameClean'].lower() in cntries:
			ndata.append(dat)
		else:
			if details:
				print dat['nameClean'] + ' not in list of cntries'
	return ndata

def intersect(*d):
	"""Find intersecting items from list of lists"""
	sets = iter(map(set, d))
	result = sets.next()
	for s in sets:
	    result = result.intersection(s)
	return result

def baseData(cntries, 
	vars=['nameClean','source','year','dataClean'], 
	matchVar='nameClean' ):
	"""Set up a base dataset to which
	we can combine other lists of 
	dictionaries"""
	data=[]
	for cntry in cntries:
		baseDict=dict.fromkeys( vars )
		baseDict[matchVar]=cntry
		baseDict['source']=''
		baseDict['year']=''
		baseDict['dataClean']=[]
		data.append(baseDict)
	return data

def combineDicts(lFiles):
	"""Combine lists of dictionaries"""
	finDict=[]
	for files in lFiles:
		print('\n\tMerging: ' + ' and '.join(files) + '\n')
		dataFiles=[loadJSON(x) for x in files]

		# Generate unique country name 
		# and remove cntries not in polity countries list
		cdataFiles=[cname(x, details=False) for x in dataFiles]
		ccdataFiles=[subsetDictByCntry(x) for x in cdataFiles]

		# Pull out intersection of countries 
		# and generate base of dataset
		dataCntries=[set(dictPull(x, 'nameClean')) for x in ccdataFiles]
		dCntries=list(set.intersection(*dataCntries))
		base=baseData(cntries=dCntries)

		# Match in countries from other lists
		for jj in range(0, len(ccdataFiles)):
			for ii in range(0,len(base)):
				cntry=base[ii]['nameClean']
				dPos=dictPull(ccdataFiles[jj],'nameClean').index(cntry)
				base[ii]['dataClean'].extend(dictPull(ccdataFiles[jj],'dataClean')[dPos])
				base[ii]['source']=base[ii]['source'] + '_' + dictPull(ccdataFiles[jj],'source')[dPos]
				base[ii]['year']=base[ii]['year'] + '_' + dictPull(ccdataFiles[jj],'year')[dPos]
			print('\t\tMerged: ' + files[jj])
		finDict.append(base)
	return finDict

def saveJSON(data, filename):
	print '\n Data for ' + filename + ' saved \n'	
	f=open(filename, 'wb')
	json.dump(data, f, sort_keys=True)
	f.close()