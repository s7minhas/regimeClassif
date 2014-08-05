pathData='/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Results'
setwd(pathData)

###
# Helpful functions
char=function(x){as.character(x)}
num=function(x){as.numeric(as.character(x))}

# Loading data
# src is 'Shr-FH' or 'All'
# yr is '99-12' or '02-12'
# wdow is 0, 1, 2, or 3
# type is unit or tpcs
loadData=function(wdow, src, yrs, type){
	ldFile=paste0(
		paste(type, yrs, src, 
			paste0('wdow',wdow),sep='_') ,'.csv')
	cat(paste0('\nLoading ',ldFile,'...\n\n'))
	read.csv(ldFile)
}
###

# Load data
# uData=loadData(1, 'Shr-FH', '99-12', 'unit')
# tData=loadData(1, 'Shr-FH', '99-12', 'tpcs')

uData=loadData(1, 'All', '02-12', 'unit')
tData=loadData(1, 'All', '02-12', 'tpcs')

nTopics=length(unique(tData$Topic))-1
yrs=unique(uData$Year)

# Getting descriptive stats of topic dist over time
tabRes=matrix(0, nrow=nTopics+1, ncol=length(yrs))
rownames(tabRes)=char(0:nTopics); colnames(tabRes)=char(yrs)

for(yr in 1:length(yrs)){
	slice=uData[which(uData$Year %in% yrs[yr]),]
	tabYr=table(slice$MaxTopic)
	tab=matrix(0, nrow=nTopics+1, ncol=1); rownames(tab)=char(0:nTopics)
	for(row in 0:nTopics){ 
		if( !is.na( tabYr[char(row)] ) ){ 
			tab[char(row),]=tabYr[char(row)] }
	}
	tabRes[,yr]=tab
}

tabRes