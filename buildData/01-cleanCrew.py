# -*- coding: utf-8 -*-

import nltk
import nltk.data, nltk.tag
tagger = nltk.data.load(nltk.tag._POS_TAGGER)
import os
import re
import json
import string
from collections import defaultdict
from compiler.ast import flatten
import datetime

#### Master function
def prepForLDA(filename, inPath, outPath):
	"""Main function to clean raw scraped data """
	os.chdir(inPath)
	jsonData=loadJSON(filename, details=True)
	data=dictPull(jsonData, 'data')
	data=removeSctnHdr(filename, data)
	data=removeURL(data)
	data=removeHTML(data)
	cntries=dictPull(jsonData, 'name')

	time()
	stClean=removePunct(data)
	stClean=tokenize(stClean)
	stClean=remNouns(stClean)
	stClean=remACR(stClean)
	stClean=remCommonWords(stClean, cntries)
	stClean=remNum(stClean)
	stClean=lemmatize(stClean)
	stClean=infqWrdStry(stClean)
	stClean=infqWrdStries(stClean)
	stClean=remCommonWords(stClean, cntries)
	time()
	
	jsonDataFin=updateDict(jsonData, stClean)
	jsonDataFin=cleanDict(jsonDataFin)
	os.chdir(outPath)
	saveJSON(jsonDataFin, filename, details=True, newName=True)

### Helper functions
def time():
	print '\t\t'+datetime.datetime.now().time().isoformat()

def ListOfFiles(stuff):
	"""Creates list of files to load 
	from a dictionary with source and year info"""
	files=[]
	for ii in range(0,len(stuff)):
		files.append([stuff[ii]['name'] + '_' + str(x) + '.json'
			for x in stuff[ii]['years']])
	return flatten(files)

def loadJSON(file, details=False):
	"""Load json file"""
	if details:
		print 'Cleaning Data for ' + file + '...\n'	
	return json.load(open(file, 'rb'))

def dictPull(dataDict, key):
	"""Pull out specific values 
	from a dictionary into a list"""
	info=[]
	for dat in dataDict:
		info.append(dat[key].encode('utf-8'))
	return info

def removeSctnHdr(filename, data):
	"""Remove source specific section headers"""
	if filename.split('_')[0]=='FH':
		return [re.sub('\n.*?:&nbsp;',' ',dat)
			for dat in data]
	elif filename.split('_')[0]=='StateHR':
		data=[re.sub('\nPDF.*?SUMMARYShare',' ',dat,flags=re.DOTALL)
			for dat in data]
		data=[re.sub('\n\n\t\t.*?\n\n',' ',dat,flags=re.DOTALL)
			for dat in data]
		for ii in range(0,len(data)):
			for letter in string.ascii_lowercase:
				data[ii]=re.sub('\n'+letter+'..*?\n',' ', 
					data[ii], flags=re.DOTALL)
		return data
	elif filename.split('_')[0]=='StateRF':
		data=[re.sub('\nPDF.*?SummaryShare',' ',dat,flags=re.DOTALL)
			for dat in data]
		data=[re.sub('\n\n\nSection.*?&nbsp;\n',' ',dat,flags=re.DOTALL)
			for dat in data]	
		return data
	else:
		return data

def noURL(string):
	"""Identify URLs in text"""
	return re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', string)

def removeURL(data):
	"""Remove URLs from text"""
	return [noURL(dat) for dat in data]

def removeHTML(data):
	"""Clean up html"""
	return [nltk.clean_html(dat) for dat in data]

def removePunct(stories):
	"""Remove punctuation and html leftovers"""
	puncts=string.punctuation
	repPunct = string.maketrans(string.punctuation, ' '*len(string.punctuation))
	storiesNoPunct = [story.translate(repPunct) for story in stories]
	storiesNoPunct = [ re.sub(
				r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', story)
				for story in storiesNoPunct  ]
	otherPunct=['nbsp','lsquo','rsquo','ldquo', 'rdquo','quot','eacute']
	for slash in otherPunct:
		storiesNoPunct=[story.replace(slash, " ") for story in storiesNoPunct]
	print('\tPunctuation removed...')
	return storiesNoPunct

def tokenize(stories):
	"""Create tokens from text"""
	storiesToken = [[word for word in story.split()] for story in stories]
	print('\tTokenized...')
	return storiesToken

def remWrd(stories, wrds, keepWrds=True):
	"""Fast way to remove items in list from
	another list"""
	nStories=[]
	for ii in range(0,len(stories)):
		story=stories[ii]
		if len(wrds)==len(stories):
			sWrds=set(wrds[ii]).intersection(story)
		else:
			sWrds=set(wrds).intersection(story)
		if keepWrds:
			nStory=[word for word in story if word in sWrds]
		else:
			nStory=[word for word in story if word not in sWrds]			
		nStories.append(nStory)
	return nStories

# def remNouns(stories):
# 	"""Remove proper nouns"""
# 	allStories=list(set(flatten([x for x in stories])))
# 	lTokens=tagger.tag(allStories)
# 	pnouns=[tok[0] for tok in lTokens if tok[1]=='NNP']
# 	storiesNoNoun = remWrd(stories, pnouns, keepWrds=False)
# 	print('\tProper Nouns removed...')
# 	return storiesNoNoun

def remNouns(stories):
	"""remmove upper case words"""
	print('\tUpper case words removed...')
	return [[word for word in story if not word[0].isupper()]
		for story in stories]

def propUpper(string):
	"""Helper to remove acronyms"""
	return sum(1. for l in string if l.isupper() )/len(string)

def remACR(stories):
	"""Remove acronyms and make all words lowercase"""
	storiesNoACR=[[word for word in story if propUpper(word)<0.5]
		for story in stories]
	storiesLower=[[word.lower() for word in story] 
		for story in storiesNoACR]
	print('\tAcronyms removed & tokens now lower cased...')
	return storiesLower

def remCommonWords(stories, cntryNames):
	"""Remove common, irrelevant words"""
	remove=nltk.corpus.stopwords.words('english')
	remove.extend(
		( [x.lower() for x in cntryNames],
			'document', 'end', 'web', 'facto',
			'examining','compared','whereabouts',
			'inspectorate','examination',
			'year', 'years','month','months',
			'day', 'days',
			'january','february','march','april','may',
			'june','july','august','september','october',
			'november','december',
			'one','two','three','four','five','six','seven',
			'eight','nine','ten','grand',
			'north','east','south','west',
			'southeast','eastern','southern','northern',
			'department','see','findings',
			'new', 'old', 'men', 'man', 'sun',
			'eye','ear','cut','although','though',
			'country','received','report','edition',
			'ombudsman',
			# 'gendarme','gendarmerie',
			'territory','province','provincial','federal',
			'mainland','canton','cantonal','island','county',
			'principality','prefecture','governorates',
			'municipality','directorate',
			'riyal','franc','euro','shilling','dirham','rial',
			'russian','lira','ruble','dinar','peso','rupee',
			'koruna','dollar',
			'ethiopian','macedonian','colombian','japanese',
			'african','philippine','emirate',
			'aire','antilles','ath','aire','birr','del',
			'indigenous','neo','lei','dust'  ) )
	remove=flatten(remove)
	storiesNoStop = remWrd(stories, remove, keepWrds=False)
	storiesNoStop = [[word for word in story if len(word)>2]
		for story in storiesNoStop]
	print('\tStop words removed...')	
	return storiesNoStop

def remNum(stories):
	"""Remove tokens that are numbers"""
	storiesNoNum = [[word for word in story if not word.isdigit()]
		for story in stories]
	print('\tNumbers removed...')
	return storiesNoNum	

def lemmatize(stories):
	"""Lemmatize"""
	wnl = nltk.stem.WordNetLemmatizer()
	storiesLemm = [[wnl.lemmatize(word) for word in story]
		for story in stories]
	print('\tLemmatized...')
	return storiesLemm

def getFreqWds(stories):
	"""Calculate frequency of words
	within a story"""
	wordCounts=[]
	for story in stories:
		wordStory=defaultdict(int)
		for word in story:
			wordStory[word]+=1
		wordCounts.append(wordStory)
	return wordCounts

def getFreqWdsAll(stories):
	"""Calculate frequency of words
	across stories"""
	wordStory=defaultdict(int)
	for story in stories:
		for word in list(set(story)):
			wordStory[word]+=1
	return wordStory	

def freqWds(wordCounts, fval=1):
	"""Return list of frequently used words in texts"""
	return [[key for key,value in wordFreq.items() if value>fval]
		for wordFreq in wordCounts]

def infqWrdStry(stories):
	"""Remove infrequent words from a story"""
	wordCounts=getFreqWds(stories)	
	toKeep=freqWds(wordCounts)
	storiesFin=remWrd(stories, toKeep, keepWrds=True)
	print('\tRemoved words occurring infrequently within a story...')
	return storiesFin

def infqWrdStries(stories):
	"""Remove infrequent words across stories"""
	wordStory=getFreqWdsAll(stories)
	freqWords=[key for key,value in wordStory.items() if value>1]
	storiesFin=remWrd(stories, freqWords, keepWrds=True)
	print('\tRemoved words occurring infrequently across stories...')
	return storiesFin

def updateDict(jsonListDict, storiesClean):
	"""Update dictionary with new data as key, value"""
	for ii in range(0,len(jsonListDict)):
		jsonListDict[ii]['dataClean'] = storiesClean[ii]
	return jsonListDict

def cleanDict(jsonListDict):
	"""Remove empty items in dictionary"""
	return [x for x in jsonListDict if len(x['dataClean'])!=0]

def saveJSON(data, filename, details=False, newName=False):
	"""save data as json"""
	if details:
		print '\n Data for ' + filename + ' cleaned \n'	
	if newName:
		filename=filename.split('.')[0] + '_Clean.json'
	f=open(filename, 'wb')
	json.dump(data, f, sort_keys=True)
	f.close()

### Running code
baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif/'

# FH (98-14), FHpress (02-13), StateHR (99-13), StateRF (01-12)
files=[{'name':'FH','years':range(1998,2000)},
		{'name':'FH','years':range(2001,2015)},
		{'name':'FHpress','years':range(2002,2014)},
		{'name':'StateHR','years':range(1999,2014)},
		{'name':'StateRF','years':range(2001,2013)}]

toClean=ListOfFiles(files)

# Clean each file
for file in toClean:
	prepForLDA(file, 
		baseDrop+'Data/Raw',
		baseDrop+'Data/forLDA')