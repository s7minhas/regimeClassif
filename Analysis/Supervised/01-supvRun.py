import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from scipy.sparse import csr_matrix, hstack

from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import precision_score as getPrec
from sklearn.metrics import recall_score as getRecall
from sklearn.metrics import f1_score as getF1
from sklearn.metrics import accuracy_score as getAcc
from sklearn.metrics import classification_report as classScore

baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

os.chdir(baseGit+'/Analysis/Supervised')
from bldTrTe import *

def prStats(modelName, actual, pred):
	print modelName
	print '\t\tPrecision: ' + str(getPrec(actual, pred))
	print '\t\tRecall: ' + str(getRecall(actual, pred))
	print '\t\tF1: ' + str(getF1(actual, pred))
	print '\t\tAccuracy: ' + str(getAcc(actual, pred))
	print '\t\t'+modelName+' Class Level:'
	print classScore(actual, pred)

def runAnalysis(trainFilename, trainYr, testFilename, testYr,
	labelFilename, labelCol, labelName,
	addWrdCnt=False):

	#### Load data
	trainData=buildData(
		textFile=trainFilename, sYr=trainYr,
		labelFile=labelFilename)

	testData=buildData(
		textFile=testFilename, sYr=testYr,
		labelFile=labelFilename)
	####

	#### Divide into train and test and convert
	# to appropriate format
	vectorizer = TfidfVectorizer()

	xTrain=vectorizer.fit_transform( trainData[:,1] )
	wTrain=csr_matrix( np.array( list(trainData[:,2]) ) ).transpose()
	if(addWrdCnt): 
		xTrain=hstack((xTrain, wTrain))
	yTrain=np.array([int(x) for x in list(trainData[:,labelCol])])

	xTest=vectorizer.transform(testData[:,1])
	wTest=csr_matrix( np.array( list(testData[:,2]) ) ).transpose()
	if(addWrdCnt):
		xTest=hstack((xTest, wTest))
	yTest=np.array([int(x) for x in list(testData[:,labelCol])])
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
	os.chdir(baseDrop+'/Results/Supervised')
	outName=labelName+'_train'+trainFilename.split('_')[1]+'_test'+testFilename.split('_')[1]+'.txt'
	orig_stdout = sys.stdout	
	f=open(outName, 'w')
	sys.stdout=f
	print '\nTrain Data: ' + trainFilename
	print 'Test Data: ' + testFilename + '\n'
	print '\nTrain Data Rows: ' + str(xTrain.shape[0])
	print 'Test Data Rows: ' + str(xTest.shape[0]) + '\n'	
	prStats('Naive Bayes', yTest, yPredNB)
	prStats('SVM', yTest, yPredSVM)
	# prStats('Logit', yTest, yPredLogit)
	f.close()
	sys.stdout = orig_stdout
	##### 

runAnalysis(
	trainFilename='train_99-08_Shr-FH_wdow0.json', trainYr=1999, 
	testFilename='test_09-13_Shr-FH_wdow0.json', testYr=2009,
	labelFilename='demData_99-13.csv', labelCol=3, labelName='democ',
	addWrdCnt=False
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json', trainYr=1999, 
	testFilename='test_07-10_Shr-FH_wdow0.json', testYr=2007,
	labelFilename='mmpData_99-10.csv', labelCol=3, labelName='monarchy',
	addWrdCnt=False
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json', trainYr=1999, 
	testFilename='test_07-10_Shr-FH_wdow0.json', testYr=2007,
	labelFilename='mmpData_99-10.csv', labelCol=4, labelName='military',
	addWrdCnt=False
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json', trainYr=1999, 
	testFilename='test_07-10_Shr-FH_wdow0.json', testYr=2007,
	labelFilename='mmpData_99-10.csv', labelCol=5, labelName='party',
	addWrdCnt=False
	)