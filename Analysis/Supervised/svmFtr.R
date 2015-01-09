# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

# Generate term matrices
svmTermSignMatrix=function(gram, var){
	# Load data
	ftrFile=getFilename(gram, var, ext='._wrdFtr.csv')
	data=read.csv( ftrFile, header=TRUE )

	# Word clouds of positive and negative words
	coefs=unique(substrRight(names(data), 1))
	
	# Output
	lapply(coefs, function(coef){
		dat=data[,which(substrRight(names(data), 1) == coef)]
		posTrms=dat[which(dat[,3]=='pos'),2]
		negTrms=dat[which(dat[,3]=='neg'),2]
		tsm=matrix(0, nrow=length(dat[,2]), ncol=2, 
			dimnames=list(dat[,2],c('Positive', 'Negative')))
		tsm[match(posTrms, rownames(tsm)),1]=dat[match(posTrms, dat[,2]),1]
		tsm[match(negTrms, rownames(tsm)),2]=abs(dat[match(negTrms, dat[,2]),1])
		tsm
		})
}

# Run function
svmMats=lapply(1:length(grams), function(ii){ svmTermSignMatrix(grams[ii], vars[ii]) })
names(svmMats)=paste0(grams, vars)

# Create comparison clouds
remWords=c('generally respected', 'exit visa', 'government generally',
	'foreign worker', 'national service', 'right practice',
	'camel jockey', 'jockey', 'camel', 'percent', 'girl',
	'number', 'service', 'work', 'beat', 'bull', 'formal',
	'registration', 'student', 'woman', 'editor', 'use',
	'domestic', 'servant', 'family', 'seat', 'right', 'ethnic',
	'office', 'officer', 'area', 'level', 'continued', 'village')
clean=function(data, words=remWords, mult=5){
	data=data[which(!rownames(data) %in% words),]
	return(data*mult)
}

# polCat
cloudDat=svmMats$'2_4polCat3'
cloudDat=lapply(cloudDat, function(x){ clean(x, remWords) })

par(mfrow=c(1,3))
lapply(cloudDat, function(x){
	comparison.cloud(x,max.words=100,random.order=TRUE) })
par(mfrow=c(1,1))

# Military
par(mfrow=c(1,3))
cloudDat=svmMats$'1military'[[1]]
cloudDat=clean(cloudDat, remWords)
comparison.cloud(cloudDat, max.words=100, random.order=TRUE)

# Monarchy
cloudDat=svmMats$'1_3monarchy'[[1]]
cloudDat=clean(cloudDat, remWords)
comparison.cloud(cloudDat, max.words=100, random.order=TRUE)

# Party
cloudDat=svmMats$'1party'[[1]]
cloudDat=clean(cloudDat, remWords)
comparison.cloud(cloudDat, max.words=100, random.order=TRUE)
par(mfrow=c(1,1))