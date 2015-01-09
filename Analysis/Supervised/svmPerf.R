rm(list=ls())
set.seed(6886)
pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
pathTex='~/Research/WardProjects/regimeClassif/Paper/graphics'

# Libraries
library(ggplot2)
library(reshape2)
library(grid)
library(RColorBrewer)

# Helpful functions
char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
convNumDcol=function(data, vars){
	for(var in vars){ data[,var]=num(data[,var]) }
	return( data ) }
mapVar=function(var, old, new){
	var=char(var)
	for(ii in 1:length(old)){ var[var==old[ii]]=new[ii] }
	return ( factor(var, levels=new) ) }
getFilename=function(gram, cat, path=pathData){
	fileExt=ifelse(substring(cat, 0, 2) %in% c('de', 'po'),'_train99-08_test09-13.txt','_train99-06_test07-10.txt')		
	paste0(path, '/grams', gram, '/', cat, fileExt)	}

## Top level performance
grams=c('2_4', '1_3', '2_3', '3_5', '1_3', '1', '1')
vars=c('polCat3', 'polCat7', 'polCat', 'democ', 'monarchy', 'party', 'military')
varsClean=c('Polity (3 Categories)', 'Polity (7 Categories)', 'Polity (4 Categories)', 
	'Democracy', 'Monarchy', 'Party', 'Military')
sels=c(1,5:7)

perfData=NULL
for(ii in sels){
	texName=getFilename(grams[ii], vars[ii])
	txt=read.table(texName,sep="\n", strip.white=TRUE)	
	topLevel=char(txt[8:11,])
	stats=unlist(lapply(strsplit(topLevel, ': '), function(x) num(x[2])))
	data=cbind(grams[ii], vars[ii], rbind(stats))
	perfData=rbind(perfData, data)
}

# Clean for plotting
perfData=data.frame(perfData, row.names=NULL)
perfData=convNumDcol(perfData, 3:6)
names(perfData)=c('gram', 'cat', 'Precision', 'Recall', 'F-1 Score', 'Accuracy')
perfData$cat=mapVar(perfData$cat, vars[sels], varsClean[sels])

# Reshape data for plotting
ggData=melt(perfData[,2:ncol(perfData)], id='cat')
col=brewer.pal(9, 'Blues')[c(3,7)]
tmp=ggplot(ggData, aes(y=cat, x=variable)) 
tmp=tmp + scale_y_discrete('',expand=c(0,0)) + scale_x_discrete('',expand=c(0,0))
tmp=tmp + geom_tile(aes(fill=value), colour='white')
tmp=tmp + scale_fill_gradient(low=col[1], high=col[2], limits=c(min(ggData$value),1))
tmp=tmp + theme(axis.ticks=element_blank(), 
  legend.position='top', legend.key.width=unit(2,'cm'), legend.title=element_blank(),
  panel.border = element_blank(),
  panel.grid.major = element_blank(), panel.grid.minor = element_blank() )
tmp

## Class level performance
getClassData=function(gram, cat){
	texName=getFilename(gram, cat)
	txt=read.table(texName,sep="\n", strip.white=TRUE)
	classLevel=lapply(14:(nrow(txt)-1), function(x){
		splits=strsplit(char(txt[x,]), ' ')[[1]]
		num(splits[splits!='']) })
	classLevel=do.call('rbind', classLevel)
	colnames(classLevel)=c('class', 'precision', 'recall', 'f1', 'support')
	classLevel=data.frame(classLevel)
	classLevel$cat=cat
	return(classLevel)
}

# Clean for plotting
classData=lapply(c(1,5:7), function(ii){ getClassData(grams[ii], vars[ii])[,c(1:4, 6)] })
classData=do.call('rbind', classData)
names(classData)[2:4]=c('Precision', 'Recall', 'F-1 Score')
classData$cat=mapVar(classData$cat, vars[sels], varsClean[sels])

# Plotting
ggData=melt(classData, id=c('class', 'cat'))
tmp=ggplot(ggData, aes(y=class, x=variable)) 
tmp=tmp + scale_y_continuous('',breaks=0:max(ggData$class), labels=0:max(ggData$class), expand=c(0,0))
tmp=tmp + scale_x_discrete('', expand=c(0,0))
tmp=tmp + geom_tile(aes(fill=value), colour='white')
tmp=tmp + scale_fill_gradient(low=col[1], high=col[2], limits=c(min(ggData$value),1))
tmp=tmp + facet_wrap(~ cat, scales='free_y', ncol=2)
tmp=tmp + theme(axis.ticks=element_blank(), 
  legend.position='top', legend.key.width=unit(2,'cm'), legend.title=element_blank(),
  panel.border = element_blank(),  
  panel.grid.major = element_blank(), panel.grid.minor = element_blank() )
tmp
