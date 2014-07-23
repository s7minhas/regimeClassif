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