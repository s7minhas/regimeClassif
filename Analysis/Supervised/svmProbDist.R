# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

cleanData = function(file){
	data=read.csv(file)
	data=data[which(data$data=='test'),]
	data$cname = toupper(countrycode(data$country, 'country.name', 'country.name'))
	data$CNTRY_NAME = panel$CNTRY_NAME[match(data$cname, panel$cname)]
	return( data )	
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
	col=brewer.pal(9, brewCol)[c(3,9)]

	tmp = ggplot(ggmapData, aes(map_id=id, fill=prob))
	tmp = tmp + geom_map(map=ggmap, linetype=1, lwd=.1, color='black')
	tmp = tmp + expand_limits(x=ggmap$long, y=ggmap$lat)
	tmp = tmp + scale_fill_continuous('', limits=c(0,1), low=col[1], high=col[2])
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

changeTrack=function(data,adj=.03,brewCol='Blues',showProb=TRUE){
	byForm=formula(paste0(names(data)[4], '~cname'))
	byDat=summaryBy(byForm, data=data, FUN=mean, na.rm=TRUE)
	chngCntries=byDat[which(!byDat[,2] %in% c(0,1)),1]

	# Plot
	if(length(chngCntries)==0){ 
		print('No countries with change in test period') 
	} else {
		data=data[which(data$cname %in% chngCntries), c(1,2,4,6,7,9)]
		data=data[data$country != 'south sudan',2:ncol(data)]
		names(data)[2]='act'
		col=brewer.pal(9,brewCol)[c(3,9)]
		ggData=melt(data[,c(1,2,4,5)], id=c('CNTRY_NAME','year'))
		ggData$value[ggData$variable=='act']=ggData$value[ggData$variable=='act']+adj
		ggData$value[ggData$variable=='predSVM']=ggData$value[ggData$variable=='predSVM']-adj
		if(showProb){yBreaks=seq(0,1,.25)} else {yBreaks=c(0,1)}
	
		tmp=ggplot(ggData, aes(x=year)) + xlab('') + ylab('')
		tmp=tmp + scale_y_continuous('', limits=c(0-adj,1+adj), breaks=yBreaks)
		tmp=tmp + geom_point(aes(color=variable,shape=variable,y=value),size=4)
		tmp=tmp + scale_color_manual(values=col)
		if(showProb){tmp=tmp + geom_line(data=data, aes(x=year, y=probSVM), linetype='dashed')}
		tmp=tmp + facet_wrap(~CNTRY_NAME)
		tmp=tmp + theme(
			axis.ticks=element_blank(),
			panel.grid.minor=element_blank(),
			legend.title=element_blank(), legend.position='none',
			axis.title.y=element_text(angle=45) )
		tmp }
}

##### Analyzing predictions #####
# Pulling data from CSVs
predData=lapply(1:length(grams), function(ii){
	# Load data
	texName=getFilename(grams[ii], vars[ii], ext='.csv')
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
buildDist(polData[[1]], tikzMake=FALSE)
buildDist(binData, tikzMake=FALSE)

# Separation plots
lapply(polData[[1]], function(x) sepPlots(x, tikzMake=FALSE))
lapply(binData, function(x) sepPlots(x, tikzMake=FALSE))

# Map
lapply(polData[[1]], function(x) buildMap(x, pdfMake=FALSE))
lapply(binData, function(x) buildMap(x, year=2010, pdfMake=FALSE))

# Find all countries where ratings change in test period
lapply(polData[[1]], function(x) changeTrack(data=x))
lapply(binData, function(x) changeTrack(data=x))