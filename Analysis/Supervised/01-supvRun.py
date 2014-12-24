import os
import sys
from operator import itemgetter
from joblib import Parallel, delayed
import multiprocessing

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix, hstack
from scipy.stats import describe

from sklearn.svm import LinearSVC, SVC
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
	coefs = model.coef_.transpose()
	coefData=np.random.random_integers(0,100,n*2).reshape(n*2,1)
	for lab in range(0, coefs.shape[1]):
		coefsFtr = sorted(zip(coefs[:,lab], fNames))
		posCoefsFtr = [[x[0], x[1], 'pos'] for x in coefsFtr[:-(n + 1):-1]]
		negCoefsFtr = [[x[0], x[1], 'neg'] for x in coefsFtr[:n]]
		coefsFtr = np.vstack((posCoefsFtr, negCoefsFtr))
		coefData = np.append(coefData, coefsFtr, axis=1)
	coefData = coefData[:,1:]
	cols = ['coef'+str(x)+',ftr'+str(x)+',sign'+str(x) for x in range(1,coefs.shape[1]+1)]
	cols = ','.join(cols) + '\n'
	os.chdir(path)
	with open(filename,'wb') as f: 
		f.write(b''+cols)
		np.savetxt(f,coefData, delimiter=',',fmt="%s")

def runAnalysis(trainFilename, testFilename, labelFilename,
	labelCol, labelName, 
	trainYr=1999, testYr=2009, grams=(3,3), 
	addWrdCnt=False, addCntry=False):

	### Incorporate gram specific path 
	if grams[1]==grams[0]:
		gramDir='grams'+str(grams[1])
	if grams[1]!=grams[0]:
		gramDir='grams'+str(grams[0])+'_'+str(grams[1])

	# Create directory
	if not os.path.exists(baseDrop+'/Results/Supervised/'+gramDir):
	    os.makedirs(baseDrop+'/Results/Supervised/'+gramDir)
	###

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
	yTrain=np.array([int(x) for x in list(trainData[:,labelCol])])

	xTest=vectorizer.transform(testData[:,1])
	yTest=np.array([int(x) for x in list(testData[:,labelCol])])

	# Add other features
	if(addWrdCnt):
		wTrain=csr_matrix( np.array( list(trainData[:,2]) ) ).transpose()
		wTest=csr_matrix( np.array( list(testData[:,2]) ) ).transpose()
		
		xTrain=hstack((xTrain, wTrain))		
		xTest=hstack((xTest, wTest))

	if(addCntry):
		cntryYr=[x.split('_')[0] for x in trainData[:,0]]
		from pandas import factorize
		cntryYr = factorize(cntryYr)[0]
		cTrain=csr_matrix( np.array( list(cntryYr) ) ).transpose()
		
		cntryYr=[x.split('_')[0] for x in testData[:,0]]
		cntryYr = factorize(cntryYr)[0]
		cTest=csr_matrix( np.array( list(cntryYr) ) ).transpose()

		xTrain=hstack((xTrain, cTrain))
		xTest=hstack((xTest, cTest))
	##### 

	#### Run SVM with linear kernel
	svmClass = LinearSVC().fit(xTrain, yTrain)
	yConfSVM = list(svmClass.decision_function(xTest))
	yPredSVM = svmClass.predict(xTest)

	svmClass_2 = SVC(kernel='linear',probability=True).fit(xTrain, yTrain)
	yProbSVM = svmClass_2.predict_proba(xTest)
	##### 

	##### Performance stats
	os.chdir(baseDrop+'/Results/Supervised/'+gramDir)
	if addWrdCnt:
		outName=labelName+'_train'+trainFilename.split('_')[1]+'_test'+testFilename.split('_')[1]+'_xtraFt'+'.txt'
	else:
		outName=labelName+'_train'+trainFilename.split('_')[1]+'_test'+testFilename.split('_')[1]+'.txt'
	orig_stdout = sys.stdout
	out=open(outName, 'w')
	sys.stdout=out
	print '\nTrain Data from: ' + trainFilename
	print '\t\tTrain Data Cases: ' + str(xTrain.shape[0])
	print '\t\tMean of y in train: ' + str(round(describe(yTrain)[2],3)) + '\n'
	print 'Test Data from: ' + testFilename
	print '\t\tTest Data Cases: ' + str(xTest.shape[0])	
	print '\t\tMean of y in test: ' + str(round(describe(yTest)[2],3)) + '\n'
	prStats('SVM', yTest, yPredSVM)
	out.close()
	sys.stdout = orig_stdout
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
	
	if labelName == 'polCat':
		probSVM=[';'.join(['%s' % x for x in row]) for row in yProbSVM]
		confSVM=[';'.join(['%s' % x for x in sublist]) for sublist in yConfSVM]
	if labelName != 'polCat':
		probSVM = [x[1] for x in yProbSVM]
		confSVM = yConfSVM

	filler=[-9999]*trainData.shape[0]
	predSVM=np.array( [[x] for x in flatten([filler, list(yPredSVM)]) ] )	
	probSVM=np.array( [[x] for x in flatten([filler, probSVM]) ] )
	confSVM=np.array( [[x] for x in flatten([filler, confSVM]) ] )	
	
	output=np.hstack((
		np.vstack((trainCntry,testCntry)),
		np.vstack((trainYr,testYr)),
		vDat, 
		np.vstack((trainLab, testLab)),
		np.hstack((confSVM,probSVM,predSVM))
		))

	os.chdir(baseDrop+'/Results/Supervised/'+gramDir)
	outCSV=outName.replace('.txt','.csv')
	with open(outCSV,'wb') as f:
		f.write(b'country,year,data,'+labelName+',confSVM,probSVM,predSVM\n')
		np.savetxt(f,output, delimiter=',',fmt="%s")

	##### Print top features for classes from SVM
	infFeatures(baseDrop+'/Results/Supervised/'+gramDir,
		outName.replace('.txt', '._wrdFtr.csv'), vectorizer, svmClass, 500)
#####

# Set up function inputs for parallized run
demTrainFile='train_99-08_Shr-FH_wdow0.json'
demTestFile='test_09-13_Shr-FH_wdow0.json'
demLabelFile='demData_99-13.csv'
demTestYear=2009
demLabelCol1=4
demLabelName1='democ'
demLabelCol2=10
demLabelName2='polCat'

mmpTrainFile='train_99-06_Shr-FH_wdow0.json'
mmpTestFile='test_07-10_Shr-FH_wdow0.json'
mmpLabelFile='mmpData_99-10.csv'
mmpTestYear=2007
mmpLabelCol1=3
mmpLabelName1='monarchy'
mmpLabelCol2=4
mmpLabelName2='military'
mmpLabelCol3=5
mmpLabelName3='party'

params=[
	(demTrainFile, demTestFile, demLabelFile, demTestYear, demLabelCol1, demLabelName1),
	(demTrainFile, demTestFile, demLabelFile, demTestYear, demLabelCol2, demLabelName2),
	(mmpTrainFile, mmpTestFile, mmpLabelFile, mmpTestYear, mmpLabelCol1, mmpLabelName1),
	(mmpTrainFile, mmpTestFile, mmpLabelFile, mmpTestYear, mmpLabelCol2, mmpLabelName2),
	(mmpTrainFile, mmpTestFile, mmpLabelFile, mmpTestYear, mmpLabelCol3, mmpLabelName3)
	]

# Run analysis
numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(1,1)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(2,2)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(3,3)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(4,4)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(5,5)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(1,2)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(1,3)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(1,4)  ) 
	for x in params
	)

numCores=multiprocessing.cpu_count()
results = Parallel(n_jobs=numCores, verbose=100)(
	delayed(runAnalysis)(
		trainFilename=x[0], testFilename=x[1], labelFilename=x[2], 
		testYr=x[3], labelCol=x[4], labelName=x[5], grams=(1,5)  ) 
	for x in params
	)