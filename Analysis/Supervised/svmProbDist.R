# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

buildDist = function(listData, year='All', var='probSVM', catOld=NULL, catNew=NULL, binsize=.1){
	data=lapply(listData, function(x){ y=x[,c('year', var)]; y$var=names(x)[4]; y } )
	data=do.call('rbind', data)
	if(!is.null(catOld)){ data$var=mapVar(data$var, catOld, catNew) }

	if(year!='All'){ data=data[which(data$year==year),] }
	tmp = ggplot(data, aes_string(x=var))
	tmp = tmp + geom_histogram(color='grey',binwidth=binsize,aes(y=..count../sum(..count..)))
	tmp = tmp + facet_wrap(~var) 
	tmp = tmp + xlab('Estimated Probability') + ylab('Proportion')
	tmp = tmp + scale_x_continuous(breaks=seq(0,1,.25),limits=c(0,1))
	tmp+theme(
		legend.position='top', axis.ticks=element_blank(), 
		panel.grid.major=element_blank(), panel.grid.minor=element_blank() )
}

sepPlots=function(data, year='All', ggalpha=.7){
	sepData=data[,c(2,4,6)]; names(sepData)[2]=c('val')
	if(year!='All'){sepData=sepData[sepData$year==year,]}
	sepData=sepData[order(sepData$probSVM),c(2:3)]
	col=brewer.pal(9, 'Blues')[c(1,5)]
	tmp=ggplot(data=sepData,aes(ymin=0,ymax=1,xmin=0,xmax=length(probSVM),x=1:length(probSVM),y=probSVM))
	tmp=tmp + geom_rect(fill=col[1]) + geom_linerange(aes(color=factor(val))) + geom_line(lwd=0.8)
	tmp=tmp + scale_color_manual(values=col)
	tmp=tmp + scale_y_continuous('', breaks=NULL, expand=c(0,0)) 
	tmp=tmp + scale_x_continuous('', breaks=NULL, expand=c(0,0))
	tmp + theme(legend.position="none", axis.ticks=element_blank(),
	  	panel.background=element_blank(), panel.grid=element_blank())
}

buildMap = function(data, year=2012, colorVar='confSVM', brewCol='BrBG'){
	data=data[which(data$year==year),]
	wmap=cshp(date=as.Date(paste0(year,'-6-30')))
	gpclibPermit()
	ggmap=fortify(wmap, region = "CNTRY_NAME")
	ggmapData=data.frame('id'=unique(ggmap$id))
	ggmapData$prob = data[,colorVar][match(ggmapData$id, data$CNTRY_NAME)]
	col=brewer.pal(11, brewCol)[c(3,9)]
	if(colorVar=='probSVM'){gglim=c(0,1)} else { gglim=NULL}

	tmp = ggplot(ggmapData, aes(map_id=id, fill=prob))
	tmp = tmp + geom_map(map=ggmap, linetype=1, lwd=.1, color='black')
	tmp = tmp + expand_limits(x=ggmap$long, y=ggmap$lat)
	# tmp = tmp + scale_fill_continuous('', limits=gglim, low=col[1], high=col[2])
	tmp = tmp + scale_fill_gradientn(colours=col)
	tmp + theme(
		line=element_blank(),title=element_blank(),
		axis.text.x=element_blank(),axis.text.y=element_blank(),
		legend.position='top', legend.key.width=unit(4,"line"),
		panel.grid.major=element_blank(), panel.grid.minor=element_blank(), 
		panel.border=element_blank())
}
buildMap(polBinData[[1]], year=2010)
changeTrack=function(data,col,plotCntries=NULL,adj=NULL,
	yLimits=NULL, yBreaks=NULL, yLabels=NULL){
	
	if(is.null(plotCntries)){
		byForm=formula(paste0(names(data)[4], '~cname'))
		byDat=summaryBy(byForm, data=data, FUN=mean, na.rm=TRUE)
		plotCntries=byDat[which(!byDat[,2] %in% c(0,1)),1] }

	# Plot
	if(length(plotCntries)==0){ 
		print('No countries with change in test period') 
	} else {
		data=data[which(data$cname %in% plotCntries), c(1,2,4,6,7,9)]
		data=data[data$country != 'south sudan',2:ncol(data)]
		names(data)[2]='act'
		ggData=melt(data[,c(1,2,4,5)], id=c('CNTRY_NAME','year'))
		
		if(!is.null(adj)){
			ggData$value[ggData$value==1]=ggData$value[ggData$value==1]-adj
			ggData$value[ggData$value==0]=ggData$value[ggData$value==0]+adj
			yBreaks=c(0+adj,1-adj) }
		
		ggData$variable = mapVar(ggData$variable, c('act', 'predSVM'), c('Actual', 'Predicted'))
	
		tmp=ggplot(ggData, aes(x=year)) + xlab('') + ylab('')
		tmp=tmp + scale_y_continuous('', limits=yLimits, breaks=yBreaks, labels=yLabels)
		tmp=tmp + geom_point(aes(color=variable,shape=variable,y=value),size=6)
		tmp=tmp + scale_color_manual(values=col) + scale_shape_manual(values=c(15,17))
		tmp=tmp + facet_wrap(~CNTRY_NAME)
		tmp + theme(
			axis.ticks=element_blank(),
			panel.grid=element_blank(),
			legend.title=element_blank(), legend.position='top',
			axis.text.x=element_text(angle=45, hjust=1) ) }
}

##### Analyzing predictions #####
# Pulling data from CSVs
polBinData=lapply(1:length(grams), function(ii){
	# Load data
	texName=getFilename(grams[ii], vars[ii], ext='.csv')
	cleanData(texName) })
names(polBinData)=paste0(grams, vars)

# Distribution of predictions
polBinDist=buildDist(listData=polBinData, binsize=.05, 
	catOld=vars, catNew=varsClean)
makePlot(polBinDist, 'pol_bin_probDist', tex=FALSE, hgt=4, wdh=8)

# Separation plots
yearPerf='All'
lapply(polBinData, function(x){
	polBinSep=sepPlots(x) 
	filename=paste(names(x)[4],yearPerf,'sep',sep='_')
	makePlot(polBinSep, filename, hgt=1.3, wdh=4, tex=FALSE) })	

# Map
lapply(polBinData, function(x){
	binMap=buildMap(x, year=2010) 
	filename=paste(names(x)[4],2010,'map',sep='_')
	makePlot(binMap, filename, hgt=4, wdh=7, tex=FALSE) })

# Find all countries where ratings change in test period
colors=brewer.pal(9,'RdBu')[c(2,8)]
polChng=changeTrack(polBinData[[1]], colors,
	adj=.25, yLimits=c(0,1), yLabels=c(0,1))
makePlot(polChng, 'polCat_perfChange', hgt=3.5, wdh=8, tex=FALSE)

lapply(polBinData[2:4], function(x){
	binChng=changeTrack(x, colors, adj=.25, yLimits=c(0,1), yLabels=c(0,1))
	if(!is.character(binChng)){
		filename=paste(names(x)[4],'perfChange',sep='_')
		makePlot(binChng, filename, hgt=3.5, wdh=8, tex=FALSE) } })

# Showing variation ratings over tiem
tmp=polBinData[[1]]
tmp=tmp[which(tmp$cname %in% c("KENYA","TURKEY")),]
ggplot(tmp, aes(x=year, y=confSVM)) + geom_point() + facet_wrap(~CNTRY_NAME, nrow=1)

tmp=binData[[3]]
tmp=tmp[which(tmp$CNTRY_NAME %in% c('Algeria', 'Pakistan', 'Thailand')),]
ggplot(tmp, aes(x=year, y=confSVM)) + geom_point() + facet_wrap(~CNTRY_NAME, nrow=1)