rm(list=ls())
if(Sys.info()["user"]=="janus829"){
	pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Desktop/Research/WardProjects/regimeClassif/Presentations/supvSummary'
}

if(Sys.info()["user"]=="s7m"){
	pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
	pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
	pathTex='~/Research/WardProjects/regimeClassif/Presentations/supvSummary'
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

buildDist = function(data, year='All', var='probSVM', tikzMake=TRUE){
	if(year!='All'){ data=data[which(data$year==year),] }
	tmp = ggplot(data, aes_string(x=var))
	tmp = tmp + geom_histogram(color='grey')
	tmp = tmp + xlab('Estimated Probability') + ylab('Frequency')
	tmp = tmp + scale_x_continuous(breaks=seq(0,1,.25),limits=c(0,1))
	tmp=tmp+theme(
		legend.position='top', axis.ticks=element_blank(), 
		panel.grid.major=element_blank(), panel.grid.minor=element_blank(),
		panel.border = element_blank(), axis.line = element_line(color = 'black'))	
	if(tikzMake){ 
		filename=paste(names(data)[4],year,'bar',sep='_')
		makePlot(tmp, filename) 
	} else {
		tmp
	}	
}

sepPlots = function(data, prob, true, tikzMake=TRUE, 
	sname=paste0(names(data)[4],'_sep'), w=7,h=3, xlabel='', title='', 
	c0=rgb(189, 201, 225,maxColorValue=255), c1=rgb(4, 90, 141,maxColorValue=255)){
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
		makePlot(tmp, filename, hgt=8, wdh=12, pdf=TRUE) 
	} else {
		tmp
	}
}

##### Analyzing predictions #####
# Pulling data from textfiles
setwd(pathData)
predData=lapply(paste0(c('polGe'),6:10,'_train99-08_test09-13.csv'),cleanData)

# Distribution of predictions
lapply(predData, function(x) buildDist(data=x, year=2012))

# Separation plots
lapply(predData, function(x) sepPlots(x, 'probSVM', 4, TRUE))

# Map
lapply(predData, function(x) buildMap(x, pdfMake=TRUE))