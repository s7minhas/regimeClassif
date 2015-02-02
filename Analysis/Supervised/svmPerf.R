# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

## Top level performance
perfData=NULL
for(ii in 1:length(grams)){
	texName=getFilename(grams[ii], vars[ii], ext='.txt')
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
perfData$cat=mapVar(perfData$cat, vars, varsClean)

# Reshape data for plotting
ggData=melt(perfData[,2:ncol(perfData)], id='cat')
col=brewer.pal(9, 'RdBu')[c(3,7)]
ggData=ggData[which(ggData$variable!='F-1 Score'),]
tmp=ggplot(ggData, aes(y=variable, x=cat)) 
tmp=tmp + scale_y_discrete('',expand=c(0,0)) + scale_x_discrete('',expand=c(0,0))
tmp=tmp + geom_tile(aes(fill=value), colour='white')
tmp=tmp + scale_fill_gradient(low=col[1], high=col[2], limits=c(min(ggData$value),1))
tmp=tmp + theme(axis.ticks=element_blank(), 
  legend.position='top', legend.key.width=unit(1.7,'cm'), legend.title=element_blank(),
  panel.border = element_blank(),
  panel.grid.major = element_blank(), panel.grid.minor = element_blank() )
makePlot(tmp, 'allAggPerf', tex=FALSE)