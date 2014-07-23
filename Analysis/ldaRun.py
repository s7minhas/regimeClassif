import os
import string
from compiler.ast import flatten
import json
import csv
from gensim import corpora, models, similarities
from operator import itemgetter

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