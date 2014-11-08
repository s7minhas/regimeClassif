rm(list=ls())
if(Sys.info()["user"]=="janus829"){
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Desktop/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

if(Sys.info()["user"]=="s7m"){
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

# Helpful libaries and functions
library(reshape)
library(ggplot2)
theme_set(theme_bw())
library(tikzDevice)

char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
extractNum=function(x){num(strsplit(char(x),':')[[1]][2])}

convNumDcol=function(data, vars){
	for(var in vars){ data[,var]=num(data[,var]) }
	return( data )
}

addLabelFactor = function(varName, varLabel, var){
	var=char(var)
	for(ii in 1:length(varName)){ var[var==varName[ii]]=varLabel[ii] }
	return( factor(var, levels=varLabel) )
}

makeTikz = function(plt, fname, path=pathTex, hgt=5, wdh=7, stnds=FALSE){
	wd=getwd(); setwd(path)
	tikz(file=fname, height=hgt, width=wdh, standAlone=stnds)
	print(plt)
	dev.off(); setwd(wd)
}

##### Aggregate measures #####
# Pulling data from textfiles
setwd(pathData)
files=NULL
dirFiles=list.files()[grepl('polGe',list.files())]
for(f in dirFiles){
	if(substr(f,nchar(f)-3,nchar(f))=='.txt'){
		files=append(files,f)
	}
}

supData=NULL
for(texfile in files){
	# Open file
	text = read.table(texfile,sep="\n", strip.white=TRUE)	
	variable=strsplit(texfile,'_')[[1]][1]
	
	# Pull out data
	results=matrix(NA, nrow=3, ncol=6, dimnames=list(NULL,
	c('Variable','Method','Precision','Recall','Fscore','Accuracy')))
	results[1,]=c( variable, 'Naive Bayes',
		unlist(lapply(8:11, function(x) FUN=extractNum(text[x,]))) )
	results[2,]=c( variable, 'SVM',
		unlist(lapply(18:21, function(x) FUN=extractNum(text[x,]))) )
	results[3,]=c(variable, 'Logit',                
	  unlist(lapply(28:31, function(x) FUN=extractNum(text[x,]))) )
  
	# Organize
	supData=rbind(supData, results)
	print(paste0(texfile, ' added to data'))	
}

# Cleaning and melting data for GG
supData=data.frame(supData)
supData=convNumDcol(supData, names(supData)[3:ncol(supData)])
ggData=melt(supData)

ggData = ggData[which(ggData$Method=='SVM' & ggData$Variable %in% paste0('polGe',7:10)),]
ggData$variable=addLabelFactor(c('Precision','Recall','Fscore','Accuracy'),
	c('Precision','Recall','F-Score','Accuracy'), ggData$variable)
ggData$Variable = addLabelFactor(paste0('polGe',7:10),
	c(paste0('Polity$\\geq$', 7:9), 'Polity$=$10'), ggData$Variable)

# Plotting
tmp=ggplot(ggData, aes(x=factor(Variable),y=value,fill=Method))
tmp=tmp+geom_bar(position="dodge",stat="identity")+scale_fill_grey("")
tmp=tmp+xlab('')+ylab('')
tmp=tmp+facet_wrap(~variable)
tmp=tmp+theme(
	legend.position='none', axis.ticks=element_blank(), 
	axis.text.x = element_text(angle = 45, hjust = 1),
	panel.grid.major=element_blank(), panel.grid.minor=element_blank()
	)
tmp
makeTikz(tmp, 'aggStats.tex')
##### End Aggregate measures #####

##### Descriptive measures #####
descData=NULL
for(texfile in files){
	# Open file
	text = read.table(texfile,sep="\n", strip.white=TRUE)	
	variable=strsplit(texfile,'_')[[1]][1]
	
	# Pull out data
	results=matrix(NA, nrow=1, ncol=3, dimnames=list(NULL,
	c('Variable','Train','Test')))
	results[1,]=c( variable, extractNum(text[3,]), extractNum(text[6,]) )
	
	# Organize
	descData=rbind(descData, results)
	print(paste0(texfile, ' added to desc data'))		
}

# Cleaning and melting data for GG
descData=data.frame(descData)
descData=convNumDcol(descData, c('Train', 'Test'))
ggData=melt(descData)

ggData = ggData[which(ggData$Variable %in% paste0('polGe',7:10)),]
ggData$Variable = addLabelFactor(paste0('polGe',7:10),
	c(paste0('Polity$\\geq$', 7:9), 'Polity$=$10'), ggData$Variable)
ggData$variable = addLabelFactor(c('Train', 'Test'), 
	c('Train\\qquad\\qquad', 'Test'), ggData$variable)

# Plotting 
tmp=ggplot(ggData, aes(x=Variable, y=value, fill=variable))
tmp=tmp+geom_bar(position="dodge",stat="identity")+scale_fill_grey("")
tmp=tmp+xlab('')+ylab('Proportion of Cases')
tmp=tmp+theme(
	legend.position='top', axis.ticks=element_blank(), 
	axis.text.x = element_text(angle = 45, hjust = 1),
	panel.grid.major=element_blank(), panel.grid.minor=element_blank(),
	panel.border = element_blank(), axis.line = element_line(color = 'black')
	)
tmp
makeTikz(tmp, 'descStats.tex')
##### End Descriptive measures #####