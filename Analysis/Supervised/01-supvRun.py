
import os
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from scipy.sparse import csr_matrix, hstack
from sklearn.metrics import classification_report  as classRep
from sklearn.metrics import precision_score  as getPrec
from sklearn.metrics import recall_score  as getRecall
from sklearn.metrics import f1_score as getf1
from sklearn.metrics import accuracy_score as getAcc
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

print 'Data prep:'
trainData=buildData(
	textFile='train_99-08_Shr-FH_wdow0.json', sYr=1999,
	labelFile='demData_99-13.csv')

testData=buildData(
	textFile='test_09-13_Shr-FH_wdow0.json', sYr=2009,
	labelFile='demData_99-13.csv')
print '\t\tLoaded train and test data'
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
print '\t\tFinished preparing data'
##### 

#### Run Naive Bayes
nb_classifier = BernoulliNB().fit(xTrain, yTrain)

yPredNB = nb_classifier.predict(xTest)

print "MODEL: Binary Naive Bayes\n"

print '\t\tPrecision:\t' + str(getPrec(yTest, yPredNB))
print '\t\tRecall:\t' + str(getRecall(yTest, yPredNB))
print '\t\tf1:\t' + str(getf1(yTest, yPredNB))
print '\t\tAccuracy:\t' + str(getAcc(yTest, yPredNB))

print '\n\t\tClassification Report:'
print classRep(yTest, yPredNB)
##### 

#### Run SVM with linear kernel
from sklearn.svm import LinearSVC

svmClass = LinearSVC().fit(xTrain, yTrain)

yPredSVM = svmClass.predict(xTest)
print "MODEL: Linear SVC\n"

print '\t\tPrecision:\t' + str(getPrec(yTest, yPredSVM))
print '\t\tRecall:\t' + str(getRecall(yTest, yPredSVM))
print '\t\tf1:\t' + str(getf1(yTest, yPredSVM))
print '\t\tAccuracy:\t' + str(getAcc(yTest, yPredSVM))

print '\n\t\tClassification report:'
print classRep(yTest, yPredSVM)
##### 

##### Run logistic regression
from sklearn.linear_model import LogisticRegression

maxentClass = LogisticRegression().fit(xTrain, yTrain)

yPredLogit = maxentClass.predict(xTest)
print "MODEL: Maximum Entropy\n"

print '\t\tPrecision:\t' + str(getPrec(yTest, yPredLogit))
print '\t\tRecall:\t' + str(getRecall(yTest, yPredLogit))
print '\t\tf1:\t' + str(getf1(yTest, yPredLogit))
print '\t\tAccuracy:\t' + str(getAcc(yTest, yPredLogit))

print '\n\t\tClassification report:'
print classRep(yTest, yPredLogit)
##### 