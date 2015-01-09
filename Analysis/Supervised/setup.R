rm(list=ls())
pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
pathTex='~/Research/WardProjects/regimeClassif/Paper/graphics'
set.seed(6886)

# libraries
loadPkg=function(toLoad){
	for(lib in toLoad){
	if(! lib %in% installed.packages()[,1])
	  { install.packages(lib, repos='http://cran.rstudio.com/') }
	suppressMessages( library(lib, character.only=TRUE) ) }
}

toLoad=c('doBy', 'ggplot2', 'reshape2', 'grid', 'wordcloud',
	'RColorBrewer', 'tikzDevice', 'countrycode', 'cshapes')
loadPkg(toLoad)
theme_set(theme_bw())

# panel dataframe
load(paste0(pathOther, '/panel.rda'))

# Functions used in multiple scripts
char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}
substrRight=function(x, n){ substr(x, nchar(x)-n+1, nchar(x))}

convNumDcol=function(data, vars){
	for(var in vars){ data[,var]=num(data[,var]) }
	return( data ) }

mapVar=function(var, old, new){
	var=char(var)
	for(ii in 1:length(old)){ var[var==old[ii]]=new[ii] }
	return ( factor(var, levels=new) ) }

getFilename=function(gram, cat, ext, path=pathData){
	fileExt=ifelse(substring(cat, 0, 2) %in% c('de', 'po'),
		paste0('_train99-08_test09-13',ext),
		paste0('_train99-06_test07-10',ext))		
	paste0(path, '/grams', gram, '/', cat, fileExt)	}

makePlot = function(plt, fname, path=pathTex, hgt=5, wdh=7, tex=TRUE, stnds=FALSE, pdf=FALSE){
	wd=getwd(); setwd(path)
	if(tex){tikz(file=paste0(fname,'.tex'), height=hgt, width=wdh, standAlone=stnds)}
	if(pdf){pdf(file=paste0(fname,'.pdf'), height=hgt, width=wdh)}
	print(plt); dev.off(); setwd(wd)
}

# Global vars
grams=c('2_4', '1_3', '2_3', '3_5', '1_3', '1', '1')
vars=c('polCat3', 'polCat7', 'polCat', 'democ', 'monarchy', 'party', 'military')
varsClean=c('Polity (3 Categories)', 'Polity (7 Categories)', 'Polity (4 Categories)', 
	'Democracy', 'Monarchy', 'Party', 'Military')
sels=c(1,5:7)