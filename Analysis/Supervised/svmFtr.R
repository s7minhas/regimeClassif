rm(list=ls())
if(Sys.info()["user"]=="janus829"){
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Desktop/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

if(Sys.info()["user"]=="s7m"){
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

# Libraries
library(ggplot2)
library(reshape2)
library(grid)

# Helpful functions
char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}

convNumDcol=function(data, vars){
	for(var in vars){ data[,var]=num(data[,var]) }
	return( data )
}

# Read in ftr from csv
setwd(pathData)

## Top level performance
grams=c(1:4, '1_2', '1_3', '1_4', '1_5')

# Replace cats with just a general call, e.g.
## democ , military, polCat_, polCat3_
cats=c(3, 7, '')

gram=grams[1]
cat=cats[1]

setwd(paste0(pathData, '/grams', gram))
list.files()

ftrFile=paste0('polCat', cat, '_train99-08_test09-13._wrdFtr.csv')
ftrData=read.csv( ftrFile, header=TRUE )
head(ftrData)

# Word clouds of positive and negative words
## 
library(wordcloud)

wrds1Pos=ftrData[which(ftrData$sign1=='pos'), 'ftr1']
wrds1PosFreq=ftrData[which(ftrData$sign1=='pos'), 'coef1']

par(mfrow=c(2,2))
wordcloud(wrds1Pos, wrds1PosFreq)