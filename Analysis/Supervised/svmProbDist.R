rm(list=ls())
set.seed(6886)
pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
pathTex='~/Research/WardProjects/regimeClassif/Paper/graphics'

# Helpful libaries and functions
load(paste0(pathOther, '/panel.rda'))
library(reshape2)
library(ggplot2)
theme_set(theme_bw())
library(tikzDevice)
library(countrycode)
library(cshapes)
library(grid)
library(RColorBrewer)

char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
getFilename=function(gram, cat, path=pathData){
	fileExt=ifelse(substring(cat, 0, 2) %in% c('de', 'po'),'_train99-08_test09-13.csv','_train99-06_test07-10.csv')		
	paste0(path, '/grams', gram, '/', cat, fileExt)	}

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
	print(plt); dev.off(); setwd(wd)
}

buildDist = function(listData, year='All', var='probSVM', tikzMake=TRUE){
	data=lapply(listData, function(x){ y=x[,c('year', var)]; y$var=names(x)[4]; y } )
	data=do.call('rbind', data)
	if(year!='All'){ data=data[which(data$year==year),] }
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

sepPlots=function(data, year='All', tikzMake=TRUE, ggalpha=.7){
	sepData=data[,c(2,4,6)]; names(sepData)[2]=c('val')
	if(year!='All'){sepData=sepData[sepData$year==year,]}
	sepData=sepData[order(sepData$probSVM),c(2:3)]
	col=brewer.pal(9, 'Blues')[c(1,6)]
	tmp=ggplot(data=sepData,aes(ymin=0,ymax=1,xmin=0,xmax=length(probSVM),x=1:length(probSVM),y=probSVM))
	tmp=tmp + geom_rect(fill=col[1]) + geom_linerange(aes(color=factor(val))) + geom_line(lwd=0.8)
	tmp=tmp + scale_color_manual(values=col)
	tmp=tmp + scale_y_continuous('', breaks=seq(0,1,.25), expand=c(0,0)) 
	tmp=tmp + scale_x_continuous('', breaks=NULL, expand=c(0,0))
	tmp=tmp + theme(legend.position="none", axis.ticks=element_blank(),
	  	panel.background=element_blank(), panel.grid=element_blank())
	if(tikzMake){ 
		filename=paste(names(data)[4],year,'sep.tex',sep='_')
		makePlot(tmp, filename, hgt=3, wdh=7) 
	} else {
		tmp
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
# Combinations
grams=c('2_4', '1_3', '2_3', '3_5', '1_3', '1', '1')
vars=c('polCat3', 'polCat7', 'polCat', 'democ', 'monarchy', 'party', 'military')

# Pulling data from CSVs
predData=lapply(1:length(grams), function(ii){
	# Load data
	texName=getFilename(grams[ii], vars[ii])
	cleanData(texName) })
names(predData)=paste0(grams, vars)

# binary vars
binData=predData[5:length(predData)]

# polCat vars
polData=lapply(predData[1:3], function(catData){
	cats=unique(catData[,4])
	lapply(cats, function(cat){
		catData[,4]=ifelse(catData[,4]==cat, 1, 0)
		names(catData)[4]=paste0(names(catData)[4], '_cat', cat)
		catData$predSVM=ifelse(catData$predSVM==cat, 1, 0)
		catData$probSVM=apply(catData, 1, function(x){ num(strsplit(x['probSVM'], ';')[[1]][cat]) })
		catData$confSVM=apply(catData, 1, function(x){ num(strsplit(x['confSVM'], ';')[[1]][cat]) })
		catData
		})	
	})

# Distribution of predictions
buildDist(polData[[1]], tikzMake=TRUE)
buildDist(binData, tikzMake=TRUE)

# Separation plots
lapply(polData[[1]], function(x) sepPlots(x, tikzMake=TRUE))
lapply(binData, function(x) sepPlots(x, tikzMake=TRUE))

# Map
lapply(polData[[1]], function(x) buildMap(x, pdfMake=TRUE))
lapply(binData, function(x) buildMap(x, pdfMake=TRUE))
