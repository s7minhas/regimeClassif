setwd('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised')
rm(list=ls())

# Helpful libaries and functions
require(reshape)
require(ggplot2)
theme_set(theme_bw())

char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
extractNum=function(x){num(strsplit(char(x),':')[[1]][2])}

# Pulling data from textfiles
supData=NULL
for(texfile in list.files()){
	# Open file
	text = read.table(texfile,sep="\n", strip.white=TRUE)	
	variable=strsplit(texfile,'_')[[1]][1]
	
	# Pull out data
	results=matrix(NA, nrow=2, ncol=6, dimnames=list(NULL,
	c('Variable','Method','Precision','Recall','Fscore','Accuracy')))
	results[1,]=c( variable, 'NB',
		unlist(lapply(8:11, function(x) FUN=extractNum(text[x,]))) )
	results[2,]=c( variable, 'SVM',
		unlist(lapply(18:21, function(x) FUN=extractNum(text[x,]))) )
	
	# Organize
	supData=rbind(supData, results)
	print(paste0(texfile, ' added to data'))	
}

# Cleaning and melting data for GG
supData=data.frame(supData)
supData$Precision=num(supData$Precision); supData$Recall=num(supData$Recall)
supData$Fscore=num(supData$Fscore); supData$Accuracy=num(supData$Accuracy)
ggData=melt(supData)

# Plotting
tmp=ggplot(ggData, aes(x=Variable,y=value,fill=Method))
tmp=tmp+geom_bar(position="dodge",stat="identity")
tmp=tmp+facet_wrap(~variable)
tmp
