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
def saveDictToCSV(filename, data, keys):
	"""filename should be string and data in dictionary format """
	f=open(filename, 'wb')
	writer=csv.DictWriter(f, keys )
	writer.writer.writerow( keys )
	writer.writerows( data  )
	f.close()

def loadJSON(file):
	return json.load(open(baseDrop+'/Data/forLDA/'+file, 'rb'))

def dictPull(dataDict, key):
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

def getCntries():
	d=open(baseDrop+'/Data/Components/cntriesForAnalysis.csv', 'rb')
	reader=csv.reader(d)
	return [x.lower() for x in flatten([x for x in reader])]

def subsetDictByCntry(data, details=False):
	"""Remove countries"""
	ndata=[]
	for dat in data:
		if dat['nameClean'].lower() in getCntries():
			ndata.append(dat)
		else:
			if details:
				print dat['nameClean'] + ' not in list of cntries'
	return ndata

def baseData():
	data=[]
	for cntry in getCntries():
		baseDict=dict.fromkeys(
			['nameClean','source','year','dataClean'] )
		baseDict['nameClean']=cntry
		data.append(baseDict)
	return data

def combineDictsBySource():
	"""Combines values in dictionaries from different sources"""
files=os.listdir(baseDrop+'/Data/forLDA')
if '.DS_Store' in files: files.remove('.DS_Store')
srcs=[x.split('_')[0] for x in files]
yrs=[x.split('_')[1] for x in files]

# for yr in yrs:
yr=yrs[10]

mtchs=[i for i, x in enumerate(yrs) if x in yr]
toCombine=[files[i] for i in mtchs]
relFiles=[loadJSON(x) for x in toCombine]
baseData=baseData()

# for file in relFiles:
file=relFiles[0]
cfile=cname(file, details=True)
cfile=subsetDictByCntry(cfile)

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
nTopics = 10
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