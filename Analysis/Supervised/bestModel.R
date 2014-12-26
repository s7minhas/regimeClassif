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

# # Raw data
# csvName=paste0('polCat',cat,'_train99-08_test09-13.csv')
# data=read.csv(csvName, header=TRUE)
# data=data[which(data$predSVM!=-9999),]
# table(data[,4], data$predSVM)

## Top level performance
grams=c(1:4, '1_2', '1_3', '1_4', '1_5')
cats=c(3, 7, '')

perfData=NULL
for(gram in grams){
	setwd(paste0(pathData, '/grams', gram))
	for(cat in cats){
		texName=paste0('polCat',cat,'_train99-08_test09-13.txt')
		txt=read.table(texName,sep="\n", strip.white=TRUE)	
		topLevel=char(txt[8:11,])
		stats=unlist(lapply(strsplit(topLevel, ': '), function(x) num(x[2])))
		
		data=cbind(gram, cat, rbind(stats))
		perfData=rbind(perfData, data)
		}
	}

# Clean up data
colnames(perfData)=c('gram', 'cat', 'precision', 'recall', 'f1', 'accuracy')
perfData=data.frame(perfData, row.names=NULL)
perfData=convNumDcol(perfData, 3:6)

# Cut data if necessary
# perfData=perfData[which(perfData$cat==3),]

# Order position of gram cats
perfData$order=apply(perfData, 1, function(x) mean(num(x[3:6])))
perfData$gramCat=paste(perfData$gram, perfData$cat, sep='__')
gramCatOrder=perfData$gramCat[order(perfData$order, decreasing=TRUE)]
perfData$gramCat=factor(perfData$gramCat, levels=gramCatOrder)

# Reshape data for plotting
ggData=melt(perfData[,3:ncol(perfData)], id='gramCat')

tmp=ggplot(ggData, aes(y=gramCat, x=variable)) 
tmp=tmp + ylab('Gram-Cat') + xlab('Statistic')
tmp=tmp + geom_tile(aes(fill=value), colour='white')
tmp=tmp + theme(axis.ticks=element_blank(), 
  legend.position='top', legend.key.width=unit(2,'cm'),
  panel.grid.major = element_blank(), panel.grid.minor = element_blank() )
tmp

## Class level performance
### Compare polcat3, polCat, polCat7 within grams
