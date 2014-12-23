rm(list=ls())
if(Sys.info()["user"]=="janus829"){
	pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Desktop/Research/WardProjects/regimeClassif/Paper/graphics'
}

if(Sys.info()["user"]=="s7m"){
	pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Research/WardProjects/regimeClassif/Presentations/graphics'
}

# Helpful libaries and functions
setwd(pathOther); load('panel.rda')

library(reshape)
library(ggplot2)
theme_set(theme_bw())
library(tikzDevice)
library(countrycode)
library(separationplot)
library(cshapes)
library(grid)
library(RColorBrewer)

char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}

cleanData = function(file){
	data=read.csv(file)
	data=data[which(data$data=='test'),]
	data$cname = toupper(countrycode(data$country, 'country.name', 'country.name'))
	data$CNTRY_NAME = panel$CNTRY_NAME[match(data$cname, panel$cname)]
	return( data )	
}

makePlot = function(plt, fname, path=pathTex, hgt=5, wdh=7, tex=TRUE, stnds=FALSE, pdf=FALSE){
	wd=getwd(); setwd(path)
	if(tex){tikz(file=paste0(fname,'.tex'), height=hgt, width=wdh, standAlone=stnds)}
	if(pdf){pdf(file=paste0(fname,'.pdf'), height=hgt, width=wdh)}
	print(plt)
	dev.off(); setwd(wd)
}

addLabelFactor = function(varName, varLabel, var){
	var=char(var)
	for(ii in 1:length(varName)){ var[var==varName[ii]]=varLabel[ii] }
	return( factor(var, levels=varLabel) )
}

getPropCases=function(labels, values){
	propData=data.frame(tapply(values,labels,FUN=mean),sort(unique(labels)))
	colnames(propData)=c('actual','var')
	if(sum(rownames(propData)!=propData$var)>0){print("d'oh")}
	propData$var = addLabelFactor(paste0('polGe',6:10),
		c(paste0('Polity$=$', 6:9), 'Polity$=$10'),propData$var)
	propData
}

buildDist = function(listData, year='All', var='probSVM', tikzMake=TRUE){
	data=lapply(listData, function(x){ y=x[,c('year', var)]; y$var=names(x)[4]; y } )
	data=do.call('rbind', data)
	if(year!='All'){ data=data[which(data$year==year),] }
	data$var = addLabelFactor(paste0('polGe',6:10),
		c(paste0('Polity$\\geq$', 6:9), 'Polity$=$10'), data$var)
	tmp = ggplot(data, aes_string(x=var))
	tmp = tmp + geom_histogram(color='grey',aes(y=..count../sum(..count..)))
	tmp = tmp + facet_wrap(~var) 
	tmp = tmp + xlab('Estimated Probability') + ylab('Proportion')
	tmp = tmp + scale_x_continuous(breaks=seq(0,1,.25),limits=c(0,1))
	tmp=tmp+theme(
		legend.position='top', axis.ticks=element_blank(), 
		panel.grid.major=element_blank(), panel.grid.minor=element_blank() )	
	if(tikzMake){ 
		filename=paste0('probDist_',year)
		makePlot(tmp, filename) 
	} else {
		tmp
	}	
}

sepPlots = function(data, prob, true, tikzMake=TRUE, 
	sname=paste0(names(data)[4],'_sep'), w=7,h=3, xlabel='', title='', 
	c0=brewer.pal(9,'Blues')[3], c1=brewer.pal(9,'Blues')[9]){
	if(tikzMake){
		makePlot(plt=separationplot(data[,prob], data[,true], type = "rect", lwd1 = 3,lwd=2,
			col0 = c0, col1 = c1, xlab = xlabel, heading = title, newplot=!tikzMake),
			fname=sname, hgt=h, wdh=w)
	} else {
		separationplot(data[,prob], data[,true], type = "rect", lwd1 = 3,lwd=2,
			col0 = c0, col1 = c1, xlab = xlabel, heading = title)
	}
}

buildMap = function(data, year=2012, colorVar='probSVM', brewCol='Blues', pdfMake=TRUE){
	data=data[which(data$year==year),]
	wmap=cshp(date=as.Date(paste0(year,'-6-30')))
	gpclibPermit()
	ggmap=fortify(wmap, region = "CNTRY_NAME")
	ggmapData=data.frame('id'=unique(ggmap$id))
	ggmapData$prob = data[,colorVar][match(ggmapData$id, data$CNTRY_NAME)]

	tmp = ggplot(ggmapData, aes(map_id=id, fill=prob))
	tmp = tmp + geom_map(map=ggmap, linetype=1)
	tmp = tmp + expand_limits(x=ggmap$long, y=ggmap$lat)
	tmp = tmp + scale_fill_continuous('', limits=c(0,1),
		low=brewer.pal(9,brewCol)[3], high=brewer.pal(9,brewCol)[9])
	tmp = tmp + theme(
		line=element_blank(),title=element_blank(),
		axis.text.x=element_blank(),axis.text.y=element_blank(),
		legend.position='top', legend.key.width=unit(4,"line"),
		panel.grid.major=element_blank(), panel.grid.minor=element_blank(), 
		panel.border=element_blank())
	if(pdfMake){ 
		filename=paste(names(data)[4],year,'map',sep='_')
		makePlot(tmp, filename, hgt=4, wdh=6, pdf=TRUE) 
	} else {
		tmp
	}
}

##### Analyzing predictions #####
# Pulling data from textfiles
setwd(paste0(pathData, '/trigrams'))
predData=lapply(paste0(c('polGe'),6:10,'_train99-08_test09-13.csv'),cleanData)

# Get indiv probs and predicts for each case
for(ii in rev(1:(length(predData)-1)) ){
	predData[[ii]][,4:10] = predData[[ii]][,4:10] - predData[[ii+1]][,4:10]
}

# Distribution of actual data
actData=lapply(predData, function(x){ y=x[,c(2,4)]; y$var=names(x)[4]; y } )
actData=lapply(actData, function(x){ names(x)[2]='actual'; x })
actData=do.call('rbind', actData)
actData=actData[which(actData$year==2012),]
ggData=getPropCases(actData$var, actData$actual)

tmp=ggplot(ggData, aes(x=var, y=actual))
tmp=tmp+geom_bar(position="dodge",stat='identity')+scale_fill_grey("")
tmp=tmp+xlab('')+ylab('Proportion of Positives')
tmp=tmp+theme(
	legend.position='top', axis.ticks=element_blank(), 
	axis.text.x = element_text(angle = 45, hjust = 1),
	panel.grid.major=element_blank(), panel.grid.minor=element_blank(),
	panel.border = element_blank(), axis.line = element_line(color = 'black')
	)
tmp
makePlot(tmp, 'polStats')

# Distribution of predictions
buildDist(predData, year=2012, tikzMake=TRUE)

# Separation plots
lapply(predData, function(x) sepPlots(x, 'probSVM', 4, TRUE))

# Map
lapply(predData, function(x) buildMap(x, pdfMake=TRUE))
