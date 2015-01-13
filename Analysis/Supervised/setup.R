rm(list=ls())
pathOther='~/Dropbox/Research/WardProjects/regimeClassif/Data/Components'
pathData='~/Dropbox/Research/WardProjects/regimeClassif/Results/Supervised'
pathTex='~/Research/WardProjects/regimeClassif/Paper/graphics'
set.seed(6886)

# load/install libraries
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

makePlot = function(plt, fname, path=pathTex, hgt=5, wdh=7, tex=TRUE, stnds=FALSE){
	wd=getwd(); setwd(path)
	if(tex){tikz(file=paste0(fname,'.tex'), height=hgt, width=wdh, standAlone=stnds)}
	if(!tex){pdf(file=paste0(fname,'.pdf'), height=hgt, width=wdh)}
	print(plt); dev.off(); setwd(wd)
}

# Global vars
grams=c('2_4', '1_3', '2_3', '3_5', '1_3', '1', '1')
vars=c('polCat3', 'polCat7', 'polCat', 'democ', 'monarchy', 'party', 'military')
varsClean=c('Polity (3 Categories)', 'Polity (7 Categories)', 'Polity (4 Categories)', 
	'Democracy', 'Monarchy', 'Party', 'Military')
sels=c(3,5:7)

polCatName=c("polCat_cat1","polCat_cat2","polCat_cat3","polCat_cat4")
polCatClean=c('-10 to -6', '-5 to 0', '1 to 5', '6 to 10')

# Words for word clouds
clean=function(data, words, mult=5, remove=FALSE){
	if(!remove){data=data[which(rownames(data) %in% words),]}
	if(remove){data=data[which(!rownames(data) %in% words),]}
	return(data*mult)
}

polCat4_cat1Wrds=c('ruling family', 'royal family','political prisoner',
	'religious police', 'royal decree', 'supreme leader', 'forced labor',
	'state emergency', 'political detainee', 'restricted freedom', 'prison camp',
	'house arrest', 'restricts freedom', 'government controlled', 'tightly controlled',
	'member royal family', 'king appoints', 'political dissident', 'religious prisoner',
	'crown prince', 'neither free fair', 'banned political', 'detention without charge',
	'restricted academic freedom', 'government restricts', 'severely limit', 
	'summary execution', 'junta continued', 'severely restricts', 'insurgent group',
	'forced relocation', 'appointed king', 'blasphemy law', 'emir appoints', 
	'war zone', 'presidential election', 'constitution law', 
	'government generally respected', 'law provides', 'free fair', 'legislative election',
	'judicial system', 'election held', 'private radio station', 'high court', 
	'free fair election', 'independent judiciary', 'elected president', 
	'parliamentary democracy', 'law provides freedom', 'parliamentary election',
	'universal suffrage', 'constitution law prohibit', 'prohibits discrimination',
	'press generally respected', 'election free fair', 'law order', 
	'academic freedom cultural')

polCat4_cat2Wrds=c('ruling party', 'security force', 'civil war', 'rebel force',
	'military tribunal', 'coup leader', 'subsistence agriculture', 'military coup',
	'interim military government', 'interim government', 'transitional government',
	'genocide suspect', 'ban political', 'honor crime', 'clan militia', 
	'extrajudicial killing', 'child labor', 'coup etat', 'bloodless coup',
	'force tortured beat', 'detained journalist', 'ban political party', 
	'coup interim', 'security force tortured', 'clan fighting', 
	'held incommunicado', 'political violence', 'opposition boycott', 
	'detained opposition', 'emergency court', 'martial law', 'without trial',
	'party boycotted', 'tortured beat otherwise', 'government harassed', 
	'criminalize civil', 'election marred irregularity', 'harassed journalist',
	'penalty defamation', 'fair election held', 'periodic free fair',
	'independent judiciary generally', 'law prohibits discrimination', 
	'government generally respected', 'free fair', 'basis universal suffrage',
	'cease fire', 'union leader', 'foreign investment', 'royal family', 
	'party coalition', 'self government', 'union organization', 'free trade',
	'constitutional democracy', 'constitutional monarchy', 'press generally respected',
	'trial independent judiciary', 'legal system')

polCat4_cat3Wrds=c('coup attempt', 'military backed civilian',
	'attempted coup', 'military backed', 'shortage judge', 
	'outside government control', 'marginal government control', 'ruling coalition',
	'emergency decree', 'following coup attempt', 'presidential candidate', 
	'religious violence', 'political opposition', 'common law', 'opposition leader',
	'operating outside government', 'transitional government', 'presidential vote',
	'executive presidency', 'legal system based', 'election irregularity', 
	'constitution prohibits', 'election result', 'private press', 'limit press freedom',
	'pay bribe', 'election opposition', 'judiciary subject political', 'limit press',
	'religious discrimination', 'trade union', 'generally free fair', 
	'international monitor', 'voter intimidation', 'contested presidential', 
	'civilian government', 'constitution law', 'government generally respected',
	'death squad', 'royal family', 'political detainee', 'supreme leader', 
	'insurgent group', 'fair election held', 'government failed', 'ban political party',
	'military tribunal', 'royal decree', 'law provides equal', 'right fair trial',
	'ensure freedom speech', 'military dictatorship', 'law provides', 
	'arrested journalist', 'freedom assembly association', 'forced disappearance',
	'law prohibits', 'constitution law prohibit', 'honor killing', 'trial independent',
	'trial independent judiciary', 'parliamentary democracy', 'independent newspaper',
	'considered free fair', 'independent judiciary generally', 'secular state')

polCat4_cat4Wrds=c('government generally respected', 'law provides', 'free fair', 
	'law prohibits', 'fair election', 'free fair election', 'fair election held', 
	'constitution law', 'universal suffrage', 'parliamentary democracy', 
	'basis universal suffrage', 'independent judiciary generally', 'election held',
	'law provides freedom', 'law prohibits discrimination', 'trial independent judiciary',
	'prime minister', 'government effectively enforced', 'law provide freedom',
	'press generally respected', 'election free fair', 'democratic political system',
	'right fair trial', 'practice independent press', 'judiciary provide effective',
	'government peacefully', 'fair trial independent', 'multiparty parliamentary',
	'effective judiciary functioning', 'ensure freedom speech', 'civil war',
	'royal family', 'rebel group', 'government owned', 'political prisoner',
	'restricted freedom', 'incommunicado detention', 'royal decree',
	'military tribunal', 'without warrant', 'practiced self censorship', 'military backed',
	'military coup', 'genocide related', 'martial law', 'restricted freedom speech',
	'interim military government', 'prior coup', 'government banned',
	'ban political party', 'government harassment', 'restricted academic freedom')

remWords=c('generally respected', 'exit visa', 'government generally',
	'foreign worker', 'national service', 'right practice',
	'camel jockey', 'jockey', 'camel', 'percent', 'girl',
	'number', 'service', 'work', 'beat', 'bull', 'formal',
	'registration', 'student', 'woman', 'editor', 'use',
	'domestic', 'servant', 'family', 'seat', 'right', 'ethnic',
	'office', 'officer', 'area', 'level', 'continued', 'village',
	'cotton', 'highland', 'relative', 'person', 'sponsor', 'issue',
	'1990s', 'fornication', 'adultery', 'porter', 'township', 'rape',
	'elect', 'bomb', 'honor', 'surgical', 'taken', 'hour', 'age', 'committee',
	'school', 'reportedly', 'facility', 'regional', 'worker', 'dissident',
	'access', 'program', 'including', 'million', 'employer', 'detained',
	'former', 'traditional responsible', 'church torture', 'community',
	'fighting', 'beating', 'child maid', 'employee', 'appointed', 'respected',
	'land')