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
		tsm })
}

# Run function
svmMats=lapply(1:length(grams), function(ii){ svmTermSignMatrix(grams[ii], vars[ii]) })

# polity (>=7) and mil, mon, party
cloudDat=list( clean(svmMats[[1]][[1]], remWords, remove=TRUE),
	clean(svmMats[[2]][[1]], remWords, remove=TRUE),
	clean(svmMats[[3]][[1]], remWords, remove=TRUE),
	clean(svmMats[[4]][[1]], remWords, remove=TRUE) )
colnames(cloudDat[[1]])=paste0('Polity ', c('+', '-'))
colnames(cloudDat[[2]])=paste0('Military ', c('+', '-'))
colnames(cloudDat[[3]])=paste0('Monarchy ', c('+', '-'))
colnames(cloudDat[[4]])=paste0('Party ', c('+', '-'))

maxWrds=100
plotColors=rev(brewer.pal(9, 'RdBu')[c(2,8)])
# pdf(file=paste0(pathTex, '/pol_bin_wrdCloud.pdf'), height=4, width=7)
par(mfrow=c(2,2))
lapply(cloudDat, function(x){
	set.seed(6886)
	comparison.cloud(x,max.words=maxWrds,random.order=FALSE,title.size=1,colors=plotColors) })
par(mfrow=c(1,1))
# dev.off()