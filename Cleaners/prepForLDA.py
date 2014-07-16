import nltk
import os
import json
import string
from collections import defaultdict

# Set wd
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/')

# Loading in data from thaiclean.csv
f=open('StateHR_99-09.json', 'rb')
test=json.load(f)
f.close()
test[0]['data'].encode('utf-8')

dates=[]
sources=[]
stories=[]
with open('thaiclean.csv', 'rb') as d:
	reader=csv.reader(d)
	for row in reader:
		dates.append(row[1])
		sources.append(row[3])
		stories.append(row[4])

# Remove punctuation
puncts = list(set(string.punctuation))
storiesNoPunct = [''.join([letter for letter in story if letter not in puncts]) for story in stories]
print('Punctuation removed...')

# Tokenize
storiesToken = [[word for word in story.lower().split()] for story in storiesNoPunct]
print('Tokenized...')

# Remove stop words
stoplist=nltk.corpus.stopwords.words('english')
storiesNoStop = [[word for word in story if word not in stoplist] for story in storiesToken]
print('Stop words removed...')

# Lemmatize
wnl = nltk.stem.WordNetLemmatizer()
storiesLemm = [[wnl.lemmatize(word) for word in story] for story in storiesNoStop]
print('Lemmatized...')

# Word frequency
wordFreq=defaultdict(int)
for story in storiesLemm:
    for word in story:
        wordFreq[word]+=1
print('Calculated word frequency...')

# Remove words that only occur once
freqTokens=[key for key,value in wordFreq.items() if value>1]
storiesFin = [[word for word in story if word in freqTokens] for story in storiesLemm]
print('Removed words occurring infrequently...')

# # Write to csv
# print('Saving to CSV...')
# data=zip(dates, sources, stories, storiesFin)

# with open('thaiForLDA.csv', 'wb') as f:
# 	writer = csv.writer(f)
# 	for slice in data:
# 		writer.writerow(slice)