# helpful packages
from gensim import corpora, models, similarities
from operator import itemgetter
import json
import csv
import os
import string

# Helpful function
def saveDictToCSV(filename, data, keys):
	"""filename should be string and data in dictionary format """
	f=open(filename, 'wb')
	writer=csv.DictWriter(f, keys )
	writer.writer.writerow( keys )
	writer.writerows( data  )
	f.close()

def loadJSON(file):
	return json.load(open(file, 'rb'))

def dictPull(dataDict, key):
	info=[]
	for dat in dataDict:
		if not isinstance(dat[key], list):
			info.append(dat[key].encode('utf-8'))
		else:
			tmp=[x.encode('utf-8') for x in dat[key]]
			info.append(tmp)
	return info

def collBySource():
	"""Takes multiple lists of dictionaries and collapses
	to one list of dictionaries """

# Set wd
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Data/forLDA')

# Choose Files to run LDA on
files=os.listdir(os.getcwd())
tmp=files[1:len(files)]
srcs=[x.split('_')[0] for x in tmp]
yrs=[x.split('_')[1] for x in tmp]
mtchs=[i for i, x in enumerate(yrs) if x == "2002"]
toCombine=[files[i] for i in mtchs]

# Loading in data
data=loadJSON('FH_2006_Clean.json')
storiesFin=dictPull(data, 'dataClean')

# Setting up for LDA
dictionary = corpora.Dictionary(storiesFin)
corpus = [dictionary.doc2bow(story) for story in storiesFin]
tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

# Running LDA
print('Running LDA...')
nTopics = 12
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