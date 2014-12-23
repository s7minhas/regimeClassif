import os
import sys
from operator import itemgetter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from scipy.sparse import csr_matrix, hstack
from scipy.stats import describe

from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import precision_score as getPrec
from sklearn.metrics import recall_score as getRecall
from sklearn.metrics import f1_score as getF1
from sklearn.metrics import accuracy_score as getAcc
from sklearn.metrics import classification_report as classScore

if os.environ.get('USER')=='janus829':
	baseDrop='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif'
	baseGit='/Users/janus829/Desktop/Research/WardProjects/regimeClassif'

if os.environ.get('USER')=='s7m':
	baseDrop='/Users/s7m/Dropbox/Research/WardProjects/regimeClassif'
	baseGit='/Users/s7m/Research/WardProjects/regimeClassif'

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

def infFeatures(path, filename, vectorizer, model, n=20):
	fNames = vectorizer.get_feature_names()
	fNames = np.array( [[x] for x in fNames] )
	coefs = model.coef_.transpose()
	top = np.hstack((coefs, fNames))
	cols = ['coef'+str(x) for x in range(1,top.shape[1])]
	cols = ','.join(cols) + ',ftr\n'
	os.chdir(path)
	with open(filename,'wb') as f:
		f.write(b''+cols)
		np.savetxt(f,top, delimiter=',',fmt="%s")

def runAnalysis(trainFilename, testFilename, labelFilename,
	labelCol, labelName, 
	trainYr=1999, testYr=2009, grams=(3,3), addWrdCnt=False):

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
	vectorizer = TfidfVectorizer(ngram_range=grams)

	xTrain=vectorizer.fit_transform( trainData[:,1] )
	wTrain=csr_matrix( np.array( list(trainData[:,2]) ) ).transpose()
	if(addWrdCnt): 
		xTrain=hstack((xTrain, wTrain))
	yTrain=np.array([int(x) for x in list(trainData[:,labelCol])])

	xTest=vectorizer.transform(testData[:,1])
	if(addWrdCnt):
		wTest=csr_matrix( np.array( list(testData[:,2]) ) ).transpose()
		xTest=hstack((xTest, wTest))
	yTest=np.array([int(x) for x in list(testData[:,labelCol])])
	##### 

	#### Run SVM with linear kernel
	svmClass = LinearSVC().fit(xTrain, yTrain)
	yConfSVM = list(svmClass.decision_function(xTest))
	yPredSVM = svmClass.predict(xTest)

	svmClass_2 = SVC(kernel='linear',probability=True).fit(xTrain, yTrain)
	yProbSVM = svmClass_2.predict_proba(xTest)
	##### 

	##### Performance stats
	# os.chdir(baseDrop+'/Results/Supervised/trigrams')
	# if addWrdCnt:
	# 	outName=labelName+'_train'+trainFilename.split('_')[1]+'_test'+testFilename.split('_')[1]+'_xtraFt'+'.txt'
	# else:
	# 	outName=labelName+'_train'+trainFilename.split('_')[1]+'_test'+testFilename.split('_')[1]+'.txt'
	# orig_stdout = sys.stdout
	# out=open(outName, 'w')
	# sys.stdout=out
	print '\nTrain Data from: ' + trainFilename
	print '\t\tTrain Data Cases: ' + str(xTrain.shape[0])
	print '\t\tMean of y in train: ' + str(round(describe(yTrain)[2],3)) + '\n'
	print 'Test Data from: ' + testFilename
	print '\t\tTest Data Cases: ' + str(xTest.shape[0])	
	print '\t\tMean of y in test: ' + str(round(describe(yTest)[2],3)) + '\n'
	prStats('SVM', yTest, yPredSVM)
	# out.close()
	# sys.stdout = orig_stdout
	#####

	##### Print data with prediction
	trainCntry=np.array( [[x.split('_')[0].replace(',','')] 
		for x in list(trainData[:,0])] )
	trainYr=np.array( [[x.split('_')[1]] for x in list(trainData[ :,0 ]) ] )
	testCntry=np.array( [[x.split('_')[0].replace(',','')] 
		for x in list(testData[:,0])] )
	testYr=np.array( [[x.split('_')[1]] for x in list(testData[ :,0 ]) ] )

	vDat=np.array( [ [x] for x in flatten([
			['train']*trainData.shape[0], 
			['test']*testData.shape[0] ]) ] )

	trainLab=np.array( [[x] for x in list(trainData[ :,labelCol ])] )
	testLab=np.array( [[x] for x in list(testData[ :,labelCol ])] )

	filler=[-9999]*trainData.shape[0]
	predSVM=np.array( [[x] for x in flatten([filler, list(yPredSVM)]) ] )
	if labelName != 'polCat':
		yProbSVM1 = [x[1] for x in yProbSVM]
		probSVM=np.array( [[x] for x in flatten([filler, yProbSVM1]) ] )
		confSVM=np.array( [[x] for x in flatten([filler, yConfSVM]) ] )	
	if labelName == 'polCat':
		probSVM=[','.join(['%s' % x for x in row]) for row in yProbSVM]
		probSVM=np.array( [[x] for x in flatten([filler, probSVM]) ] )
		confSVM=[','.join(['%s' % x for x in sublist]) for sublist in yConfSVM]
		confSVM=np.array( [[x] for x in flatten([filler, confSVM]) ] )
	output=np.hstack((
		np.vstack((trainCntry,testCntry)),
		np.vstack((trainYr,testYr)),
		vDat, 
		np.vstack((trainLab, testLab)),
		npf.hstack((confSVM,probSVM,predSVM))
		))

	os.chdir(baseDrop+'/Results/Supervised/trigrams')
	outCSV=outName.replace('.txt','.csv')
	with open(outCSV,'wb') as f:
		f.write(b'country,year,data,'+labelName+',confSVM,probSVM,predSVM\n')
		np.savetxt(f,output, delimiter=',',fmt="%s")

	##### Print top features for classes from SVM
	infFeatures(baseDrop+'/Results/Supervised/trigrams', 
		outName.replace('.txt', '._wrdFtr.csv'), vectorizer, svmClass, 100)
#####

runAnalysis(
	trainFilename='train_99-08_Shr-FH_wdow0.json',
	testFilename='test_09-13_Shr-FH_wdow0.json',
	labelFilename='demData_99-13.csv', 
	labelCol=4, labelName='democ'
	)

runAnalysis(
	trainFilename='train_99-08_Shr-FH_wdow0.json',
	testFilename='test_09-13_Shr-FH_wdow0.json',
	labelFilename='demData_99-13.csv', 
	labelCol=10, labelName='polCat'
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json',
	testFilename='test_07-10_Shr-FH_wdow0.json',
	labelFilename='mmpData_99-10.csv', 
	testYr=2007, labelCol=3, labelName='monarchy'
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json',
	testFilename='test_07-10_Shr-FH_wdow0.json',
	labelFilename='mmpData_99-10.csv', 
	testYr=2007, labelCol=4, labelName='military'
	)

runAnalysis(
	trainFilename='train_99-06_Shr-FH_wdow0.json',
	testFilename='test_07-10_Shr-FH_wdow0.json',
	labelFilename='mmpData_99-10.csv', 
	testYr=2007, labelCol=5, labelName='party'
	)