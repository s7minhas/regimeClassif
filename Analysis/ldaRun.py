import os
import re
import string
from compiler.ast import flatten
import json
import csv
from gensim import corpora, models, similarities
from operator import itemgetter
import datetime

#### Master function
def runLDAs(filename, nTopics=12, addClean=False, save=True):
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
			print 'do stuff'

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
					'Dates':year, 'Sources':source, 
					'TopicProbMix':ldaOUT[corpus[ii]],
					'MaxTopic':max(ldaOUT[corpus[ii]],key=itemgetter(1))[0] } 
					for ii in range(0, len(reports)) ]
		STRYDAT.append(storyData)
	
	if save:
		print('\t\tWriting results to CSV...')
		os.chdir(baseDrop+'/Results')
		TPCDAT=flatten(TPCDAT)
		STRYDAT=flatten(STRYDAT)
		saveDictToCSV( cleanName(filename, 'tpcs'), TPCDAT, 
			['Topic', 'Terms'] )
		saveDictToCSV(cleanName(filename, 'unit'), STRYDAT, 
			['Dates','Sources','OrigStory','ProcStory','TopicProbMix','MaxTopic'] )
	else:
		print '\t\tReturning results as list'
		return [TPCDAT, STRYDAT]

### Helpful functions
def time():
	print '\t\t'+datetime.datetime.now().time().isoformat()

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

def loadJSON(file):
	return json.load(open(file, 'rb'))

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
baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

results=runLDAs(filename='data_99-12_Shr-FH.json', 
	nTopics=12, addClean=False, save=True)
results=runLDAs(filename='data_02-12_All.json', 
	nTopics=12, addClean=False, save=True)