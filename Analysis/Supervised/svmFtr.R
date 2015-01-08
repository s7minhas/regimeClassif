rm(list=ls())
set.seed(6886)
pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
pathTex='~/Research/WardProjects/regimeClassif/Presentations/supvSummary'

# Libraries
library(ggplot2)
library(reshape2)
library(grid)
library(wordcloud)

# Helpful functions
char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
substrRight=function(x, n){ substr(x, nchar(x)-n+1, nchar(x))}

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

gram=grams[3]
cat=cats[1]

setwd(paste0(pathData, '/grams', gram))
list.files()

ftrFile=paste0('polCat', cat, '_train99-08_test09-13._wrdFtr.csv')
ftrData=read.csv( ftrFile, header=TRUE )

# Word clouds of positive and negative words
getWords=function(data, sign){
	coefs=unique(substrRight(names(data), 1))
	lapply(coefs, function(coef){
		slice = data[which(data[,paste0('sign', coef)]== sign), ]
		slice[,c(paste0('ftr', coef), paste0('coef', coef))]
		})
}

par(mfrow=c(2,2))
lapply(getWords(ftrData, 'pos'), function(x){
	coefCut=quantile(x[,2], .25)
	x=x[which(x[,2] >= coefCut),]
	wordcloud(x[,1], x[,2])	
	})