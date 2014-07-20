import nltk
import os
import re
import json
import string
from collections import defaultdict
from compiler.ast import flatten

def prepForLDA(filename, inPath, outPath):
	os.chdir(inPath)
	jsonData=loadJSON(filename)
	data=dictPull(jsonData, 'data')
	cntries=dictPull(jsonData, 'name')

	stClean=removePunct(data)
	stClean=tokenize(stClean)
	stClean=remWords(stClean, cntries)
	stClean=remNum(stClean)
	stClean=lemmatize(stClean)
	stClean=infqWrdStry(stClean)
	stClean=infqWrdStries(stClean)

	jsonDataFin=updateDict(jsonData, stClean)
	os.chdir(outPath)
	saveJSON(jsonDataFin, filename)

def ListOfFiles(stuff):
	files=[]
	for ii in range(0,len(stuff)):
		files.append([stuff[ii]['name'] + '_' + str(x) + '.json'
			for x in stuff[ii]['years']])
	return flatten(files)

def loadJSON(file):
	print 'Cleaning Data for ' + file + '...\n'	
	return json.load(open(file, 'rb'))

def dictPull(dataDict, key):
	info=[]
	for dat in dataDict:
		info.append(dat[key].encode('utf-8'))
	return info

def removePunct(stories):
	puncts=string.punctuation
	repPunct = string.maketrans(string.punctuation, ' '*len(string.punctuation))
	storiesNoPunct = [story.translate(repPunct) for story in stories]
	storiesNoPunct = [ re.sub(
				r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', story)
				for story in storiesNoPunct  ]
	otherPunct=["\n", "\t", 'nbsp', 'Ratings Change', 'Overview']
	for slash in otherPunct:
		storiesNoPunct=[story.replace(slash, " ") for story in storiesNoPunct]
	print('		Punctuation removed...')
	return storiesNoPunct

def tokenize(stories):
	storiesToken = [[word for word in story.lower().split()] 
		for story in stories]
	print('		Tokenized...')
	return storiesToken

def remWords(stories, cntryNames):
	remove=nltk.corpus.stopwords.words('english')
	remove.extend(
		( [x.lower() for x in cntryNames],
			'document', 'end', 'year', 'years',
			'sri', 'lanka', 'Ivoire', 
			'january','february','march','april','may',
			'june','july','august','september','october',
			'november','december',
			'one','two','three','four','five','six','seven',
			'eight','nine','ten',
			list(string.ascii_lowercase) ) )
	remove=flatten(remove)
	storiesNoStop = [[word for word in story if word not in remove]
		for story in stories]
	print('		Stop words removed...')	
	return storiesNoStop

def remNum(stories):
	storiesNoNum = [[word for word in story if not word.isdigit()]
		for story in stories]
	print('		Numbers removed...')
	return storiesNoNum	

def lemmatize(stories):
	wnl = nltk.stem.WordNetLemmatizer()
	storiesLemm = [[wnl.lemmatize(word) for word in story]
		for story in stories]
	print('		Lemmatized...')
	return storiesLemm

def infqWrdStry(stories):
	wordCounts=[]
	for story in stories:
		wordStory=defaultdict(int)
		for word in story:
			wordStory[word]+=1
		wordCounts.append(wordStory)

	freqWords=[[key for key,value in wordFreq.items() if value>1]
		for wordFreq in wordCounts]
	freqWords=flatten(freqWords)
	storiesFin = [[word for word in story if word in freqWords]
		for story in stories]
	print('		Removed words occurring infrequently within a story...')
	return storiesFin

def infqWrdStries(stories):
	wordStory=defaultdict(int)
	for story in stories:
		for word in list(set(story)):
			wordStory[word]+=1

	freqWords=[key for key,value in wordStory.items() if value>1]
	storiesFin = [[word for word in story if word in freqWords]
		for story in stories]
	print('		Removed words occurring infrequently across stories...')
	return storiesFin

def updateDict(jsonListDict, storiesClean):
	for ii in range(0,len(jsonListDict)):
		jsonListDict[ii]['dataClean'] = storiesClean[ii]
	return jsonListDict

def saveJSON(data, filename):
	print '\n Data for ' + filename + ' cleaned \n'	
	newFilename=filename.split('.')[0] + '_Clean.json'
	f=open(newFilename, 'wb')
	json.dump(data, f, sort_keys=True)
	f.close()