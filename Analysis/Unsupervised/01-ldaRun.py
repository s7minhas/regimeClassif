import os
import re
import string
from compiler.ast import flatten
from collections import defaultdict
import json
import csv
from gensim import corpora, models, similarities
from operator import itemgetter
import datetime
import nltk
from nltk.collocations import *

#### Master function
def runLDAs(filename, gram=3, nTopics=3, save=True, 
	addClean=False, removeWords=False, rWrds=[]):
	"""Runs LDA, saves results, and contains 
	options to  perform additional cleaning """

	os.chdir(baseDrop+'/Data/forLDA')
	print '\nLoading data...\n'
	data=loadJSON(filename)
	TPCDAT=[]
	STRYDAT=[]	

	for dataYr in data:

		# Source information for dataYr
		src=[x for x in dictPull(dataYr, 'source')[0].split('_') if len(x)>0]
		if len(set(src))==4: source='All'
		else: source='_'.join( set(src) )

		# Year information for dataYr
		srcPos=[i for i, x in enumerate(src) if x[0:5] == "State"]
		yr=[x[2:4] for x in dictPull(dataYr, 'year')[0].split('_') if len(x)>0]
		yrC=sorted( set( [yr[i] for i in srcPos] ) )
		year='_'.join( [ str(x) for x in yrC ] )

		# Pulling out relevant data
		cntries=dictPull(dataYr, 'nameClean')
		reports=dictPull(dataYr, 'dataClean')

		# Additional cleaning
		if addClean:
			reports=infqWrdStry(reports)
			# reports=infqWrdStries(reports)

		# Remove extra words
		if removeWords:
			reports = remWrd(reports, rWrds, keepWrds=False)

		# incorporate varying grams
		if gram>1:
			if gram==2:
				ngramMeasures = nltk.collocations.BigramAssocMeasures()
				ngramFinder = BigramCollocationFinder
			if gram==3:
				ngramMeasures = nltk.collocations.TrigramAssocMeasures()
				ngramFinder = TrigramCollocationFinder

			reports = [ngramGet(story, ngramFinder) for story in reports]

		# Setting up for LDA
		dictionary = corpora.Dictionary(reports)
		corpus = [dictionary.doc2bow(story) for story in reports]
		tfidf = models.TfidfModel(corpus) 
		corpusTfidf = tfidf[corpus]

		# Running LDA
		print('\t\tRunning LDA for ' + year + ' from ' + source)
		ldaOUT = models.LdaModel(corpusTfidf, 
			id2word=dictionary, num_topics=nTopics)

		# Obtain topics
		topics=[]
		for topic in range(0, nTopics):
			temp = ldaOUT.show_topic(topic, 10)
			terms=[]
			for term in temp:
				terms.append(term[1])
			topics.append([", ".join(terms)])

		topicData=[ {
					'Year':year, 'Source':source,
					'Topic':ii,'Terms':topics[ii-1] 
					} 
					for ii in range(1,nTopics+1)]
		TPCDAT.append(topicData)

		# Obtain unit level topic classifications
		storyData=[ {'Cntry':cntries[ii],
					'Year':year, 'Source':source, 
					'TopicProbMix':ldaOUT[corpus[ii]],
					'MaxTopic':max(ldaOUT[corpus[ii]],key=itemgetter(1))[0] } 
					for ii in range(0, len(reports)) ]
		STRYDAT.append(storyData)
	
	if save:
		print('\t\tWriting results to CSV...')
		os.chdir(baseDrop+'/Results/LDA')
		TPCDAT=flatten(TPCDAT)
		STRYDAT=flatten(STRYDAT)
		saveDictToCSV( cleanName(filename, 'tpcs'), TPCDAT, 
			['Year','Source','Topic', 'Terms'] )
		saveDictToCSV(cleanName(filename, 'unit'), STRYDAT, 
			['Cntry','Year','Source','TopicProbMix','MaxTopic'] )
	else:
		print '\t\tReturning results as list'
		return [TPCDAT, STRYDAT]

### Helpful functions
def time():
	print '\t\t'+datetime.datetime.now().time().isoformat()

def loadJSON(file):
	return json.load(open(file, 'rb'))

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
	print('\t\t\tRemoved words occurring infrequently...')
	return storiesFin

def infqWrdStries(stories):
	"""Remove infrequent words across stories"""
	wordStory=getFreqWdsAll(stories)
	freqWords=[key for key,value in wordStory.items() if value>1]
	storiesFin=remWrd(stories, freqWords, keepWrds=True)
	print('\t\t\tRemoved words occurring infrequently across stories...')
	return storiesFin

def ngramGet(story, gramFinder):
	ngramObj = gramFinder.from_words(story)

	ngramItems = ngramObj.ngram_fd.items()
	ngrams = [' '.join(x[0]) for x in ngramItems]
	return ngrams

def cleanName(name, add, ext='.csv'):
	name2=re.sub('.json',ext,name)
	return re.sub('data',add,name2)

def saveDictToCSV(filename, data, keys):
	"""filename should be string and data in dictionary format """
	f=open(filename, 'wb')
	writer=csv.DictWriter(f, keys )
	writer.writer.writerow( keys )
	writer.writerows( data  )
	f.close()

### Running code
if os.environ.get('USER')=='janus829':
	baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
	baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

if os.environ.get('USER')=='s7m':
	baseDrop='/Users/s7m/Dropbox/Research/WardProjects/regimeClassif'
	baseGit='/Users/s7m/Research/WardProjects/regimeClassif'

uselessWrds=[]
numTopics=10

runLDAs(filename='data_99-12_Shr-FH_wdow0.json')

runLDAs(filename='data_02-12_All_wdow0.json')

runLDAs(filename='data_99-12_Shr-FH_wdow1.json')

runLDAs(filename='data_02-12_All_wdow1.json')

runLDAs(filename='data_99-12_Shr-FH_wdow2.json')

runLDAs(filename='data_02-12_All_wdow2.json')

runLDAs(filename='data_99-12_Shr-FH_wdow3.json')

runLDAs(filename='data_02-12_All_wdow3.json')