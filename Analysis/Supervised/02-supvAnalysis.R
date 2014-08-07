rm(list=ls())
if(Sys.info()["user"]=="janus829"){
	pathData='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='/Users/janus829/Desktop/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

# Helpful libaries and functions
require(reshape)
require(ggplot2)
theme_set(theme_bw())
require(tikzDevice)

char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
extractNum=function(x){num(strsplit(char(x),':')[[1]][2])}

##### Aggregate measures #####
# Pulling data from textfiles
setwd(pathData)
files=NULL
for(f in list.files()){
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
	results=matrix(NA, nrow=2, ncol=6, dimnames=list(NULL,
	c('Variable','Method','Precision','Recall','Fscore','Accuracy')))
	results[1,]=c( variable, 'Naive Bayes\\qquad\\qquad',
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

ggData$variable=char(ggData$variable)
ggData$variable[ggData$variable=='Fscore']='F-Score'
ggData$variable=factor(ggData$variable, 
	levels=c('Precision','Recall','F-Score','Accuracy'))

ggData$Variable=char(ggData$Variable)
ggData$Variable[ggData$Variable=='democ']='Democracy'
ggData$Variable[ggData$Variable=='military']='Military'
ggData$Variable[ggData$Variable=='monarchy']='Monarchy'
ggData$Variable[ggData$Variable=='party']='One-Party'

# Plotting
tmp=ggplot(ggData, aes(x=factor(Variable),y=value,fill=Method))
tmp=tmp+geom_bar(position="dodge",stat="identity")+scale_fill_grey("")
tmp=tmp+xlab('')+ylab('')
tmp=tmp+facet_wrap(~variable)
tmp=tmp+theme(
	legend.position='top', 
	axis.text.x = element_text(angle = 45, hjust = 1),
	axis.ticks=element_blank(), 
	panel.grid.major=element_blank(), panel.grid.minor=element_blank()
	)
tmp
setwd(pathTex)
tikz(file='aggStats.tex', height=5, width=7, standAlone=F)
tmp
dev.off()
##### End Aggregate measures #####

##### Descriptive measures #####
setwd(pathData)
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
descData$Train=num(descData$Train); descData$Test=num(descData$Test)
ggData=melt(descData)

ggData$Variable=char(ggData$Variable)
ggData$Variable[ggData$Variable=='democ']='Democracy'
ggData$Variable[ggData$Variable=='military']='Military'
ggData$Variable[ggData$Variable=='monarchy']='Monarchy'
ggData$Variable[ggData$Variable=='party']='One-Party'

ggData$variable=char(ggData$variable)
ggData$variable[ggData$variable=='Train']='Train\\qquad\\qquad'
ggData$variable=factor(ggData$variable, 
	levels=c('Train\\qquad\\qquad','Test'))

# Plotting 
tmp=ggplot(ggData, aes(x=Variable, y=value, fill=variable))
tmp=tmp+geom_bar(position="dodge",stat="identity")+scale_fill_grey("")
tmp=tmp+xlab('')+ylab('Proportion of Cases')
tmp=tmp+theme(
	legend.position='top', 
	axis.text.x = element_text(angle = 45, hjust = 1),
	axis.ticks=element_blank(), 
	panel.grid.major=element_blank(), panel.grid.minor=element_blank(),
	panel.border = element_blank(), axis.line = element_line(color = 'black')
	)
tmp
setwd(pathTex)
tikz(file='descStats.tex', height=5, width=7, standAlone=F)
tmp
dev.off()
##### End Descriptive measures #####