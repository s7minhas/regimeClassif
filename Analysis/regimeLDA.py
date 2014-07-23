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

# Helpful function
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
		return [[f for f in filesSrc if fhYrFix(f) in wdowYr(year, wdow)]
			for year in years]
	else: 
		return [[f for f in filesSrc if fhYrFix(f) in year]
			for year in years]

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

# years=[str(x) for x in range(1999,2014)]; sources=['StateHR','FH']
# years=[str(x) for x in range(2002,2013)]; sources=['StateHR','FH','FHpress','StateRF']
lFiles=filesToMerge(sources=['StateHR','FH'], years=range(1999,2014), window=True)

# def combineDicts():
# Load files
files=lFiles[2]
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

def saveDictToCSV(filename, data, keys):
	"""filename should be string and data in dictionary format """
	f=open(filename, 'wb')
	writer=csv.DictWriter(f, keys )
	writer.writer.writerow( keys )
	writer.writerows( data  )
	f.close()

######################
# Loading in data
os.chdir(baseDrop+'/Data/forLDA')
data=loadJSON('StateHR_2006_Clean.json')
storiesFin=dictPull(data, 'dataClean')

# Setting up for LDA
dictionary = corpora.Dictionary(storiesFin)
corpus = [dictionary.doc2bow(story) for story in storiesFin]
tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

# Running LDA
print('Running LDA...')
nTopics = 20
ldaOUT = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=nTopics)
# ldaOUT.save('ldaOUT_12Topics')

# Write topics to CSV
print('Writing results to CSV...')

topics=[]
for topic in range(0, nTopics):
	temp = ldaOUT.show_topic(topic, 10)
	terms=[]
	for term in temp:
		terms.append(term[1])
	topics.append([", ".join(terms)])

topicData=[{'Topic':ii,'Terms':topics[ii-1]} for ii in range(1,nTopics+1)]
print(topicData)
saveDictToCSV('topicsLDA.csv', topicData, ['Topic', 'Terms'])

# Write out unit level  topic classifications
storyData=[ { 'Dates':dates[ii], 'Sources':sources[ii], 
			'TopicProbMix':ldaOUT[corpus[ii]],
			'MaxTopic':max(ldaOUT[corpus[ii]],key=itemgetter(1))[0] } 
			for ii in range(0, len(storiesFin)) ]
saveDictToCSV('storiesLDA.csv', storyData, 
	['Dates','Sources','OrigStory','ProcStory','TopicProbMix','MaxTopic'] )