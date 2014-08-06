
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from scipy.sparse import csr_matrix, hstack
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score as getAcc
from sklearn.metrics import precision_recall_fscore_support as perfSumm
import numpy as np
from operator import itemgetter

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

os.chdir(baseGit+'/Analysis/Supervised')
from bldTrTe import *

#### Load data
# Parameters for data function
# textFile='train_99-08_Shr-FH_wdow0.json'; sYr=1999
# textFile='test_09-13_Shr-FH_wdow0.json'; sYr=2009

# labelFile='demData_99-13.csv'
# labelFile='mmpData_99-10.csv'

trainData=buildData(
	textFile='train_99-08_Shr-FH_wdow0.json', sYr=1999,
	labelFile='demData_99-13.csv')

testData=buildData(
	textFile='test_09-13_Shr-FH_wdow0.json', sYr=2009,
	labelFile='demData_99-13.csv')
####

#### Divide into train and test and convert
# to appropriate format
vectorizer = TfidfVectorizer()

xTrain=vectorizer.fit_transform( trainData[:,1] )
wTrain=csr_matrix( np.array( list(trainData[:,2]) ) ).transpose()
# xTrain=hstack((xTrain, wTrain))
yTrain=np.array([int(x) for x in list(trainData[:,3])])

xTest=vectorizer.transform(testData[:,1])
wTest=csr_matrix( np.array( list(testData[:,2]) ) ).transpose()
# xTest=hstack((xTest, wTest))
yTest=np.array([int(x) for x in list(testData[:,3])])
##### 

#### Run Naive Bayes
nb_classifier = BernoulliNB().fit(xTrain, yTrain)
yPredNB = nb_classifier.predict(xTest)
##### 

#### Run SVM with linear kernel
svmClass = LinearSVC().fit(xTrain, yTrain)
yPredSVM = svmClass.predict(xTest)
##### 

##### Run logistic regression
maxentClass = LogisticRegression().fit(xTrain, yTrain)
yPredLogit = maxentClass.predict(xTest)
##### 

##### Performance stats
perfAll=list(
	perfSumm(yTest, yPredNB, average=None), 
	perfSumm(yTest, yPredSVM, average=None),
	perfSumm(yTest, yPredLogit, average=None)
	)

accAll=list(
	getAcc(yTest, yPredNB),
	getAcc(yTest, yPredSVM),
	getAcc(yTest, yPredLogit)
	)
##### 