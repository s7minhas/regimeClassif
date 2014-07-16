# helpful packages
from gensim import corpora, models, similarities
from operator import itemgetter
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

# Set wd
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/ThailandStories/')

# Loading in data from thaiclean.csv
dates=[]
sources=[]
stories=[]
storiesFin=[]
with open('thaiForLDA.csv', 'rb') as d:
	reader=csv.reader(d)
	for row in reader:
		dates.append(row[0])
		sources.append(row[1])
		stories.append(row[2])
		storiesFin.append(row[3])

# Clean storiesFin
print('Loading stories for LDA...')
puncts = list(set(string.punctuation))
storiesFin = [''.join([letter for letter in story if letter not in puncts]).split() for story in storiesFin]

# Prepping for thaiLDA
print('Prepping for LDA...')
dictionary = corpora.Dictionary(storiesFin)
corpus = [dictionary.doc2bow(story) for story in storiesFin]
tfidf = models.TfidfModel(corpus) 
corpus_tfidf = tfidf[corpus]

# Running thaiLDA
print('Running LDA...')
nTopics = 12
thaiLDA = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=nTopics)
thaiLDA.save('thaiLDA_12Topics')

# Write topics to CSV
print('Writing results to CSV...')

topics=[]
for topic in range(0, nTopics):
	temp = thaiLDA.show_topic(topic, 10)
	terms=[]
	for term in temp:
		terms.append(term[1])
	topics.append([", ".join(terms)])

topicData=[{'Topic':ii,'Terms':topics[ii-1]} for ii in range(1,nTopics+1)]
saveDictToCSV('topicsLDA.csv', topicData, ['Topic', 'Terms'])

# Write out original stories with topic classifications
storyData=[ { 'Dates':dates[ii], 'Sources':sources[ii], 'OrigStory':stories[ii],
			'ProcStory':storiesFin[ii], 'TopicProbMix':thaiLDA[corpus[ii]],
			'MaxTopic':max(thaiLDA[corpus[ii]],key=itemgetter(1))[0] } 
			for ii in range(0, len(storiesFin)) ]
saveDictToCSV('storiesLDA.csv', storyData, 
	['Dates','Sources','OrigStory','ProcStory','TopicProbMix','MaxTopic'] )