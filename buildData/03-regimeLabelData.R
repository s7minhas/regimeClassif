# Script to combine different regime datasets into labels
# for supervised topic modeling

# Clear workspace and set path
rm(list=ls())
baseData='~/Dropbox/Research/WardProjects/regimeClassif/Data'

# Helpful functions
library(foreign)
library(countrycode)
char=function(x){as.character(x)}
num=function(x){as.numeric(char(x))}

### Cntries in JSON texts
setwd(paste0(baseData, '/Components'))
cntries=char(read.csv('cntriesForAnalysis.csv', header=F)[,1])
cntries=toupper(cntries)

# Generate consistent country names and subset data
# to relevant period of analysis
prepData=function(data, cvar, yvar, repError, 
	yrS, yrE, detail, keepvars, removeNAs, duplCheck){
	data=data[which(data[,yvar] %in% yrS:yrE),]
	cname=countrycode(data[,cvar],'country.name','country.name')
	cname=toupper(cname)
	data=cbind(data, cname=cname)	
	if(sum(is.na(cname))>0 & repError){
		cat('Unrecognized country names:\n')
		print(data[which(is.na(data$cname)), c(cvar,yvar,'cname')])
		} else {
			subdata=data[which(data$cname %in% cntries),]
			if(detail){
				cat('Following countries dropped:\n')
				print(setdiff(unique(data$cname),unique(subdata$cname)))
			}
			if(removeNAs){
				subdata=na.omit(subdata[,c('cname',cvar,yvar,keepvars)])
			}
			if(duplCheck){
				cat('\nDuplicates:\n')
				print(table(paste0(subdata$cname,subdata[,yvar]))
					[table(paste0(subdata$cname,subdata[,yvar]))>1])
			}
			subdata$id=paste0(subdata$cname,subdata[,yvar])
			subdata[,c('id','cname',cvar,yvar,keepvars)]
	}
 }

#############################################
##### Start Democracy Datasets #####
### DD (ends at 2008)
setwd(paste0(baseData,'/regimeData/DD'))
dd=read.csv('dd.csv')
ddFin=prepData(dd, 'ctryname', 'year', TRUE, 
	1999, 2010, TRUE, c('democracy'), TRUE, TRUE)

### BMR (ends at 2007)
setwd(paste0(baseData,'/regimeData/BMR'))
bmr=read.dta('democracy.dta')
bmr$country=char(bmr$country)
bmr$country[bmr$country=='LIECHSTENSTEIN']='liechtenstein'
bmr$country[bmr$country=='UNITED ARAB E.']='United Arab Emirates'
bmr$country[bmr$country=='EQUATORIAL G']='EQUATORIAL GUINEA'
bmr$country[bmr$country=='GUINEA-BISS']='GUINEA-BISSAU'
bmr$country[bmr$country=='SAMOA, W']='SAMOA'
bmr$country[bmr$country=='PAPUA N.GUINEA']='PAPUA New GUINEA'
bmrFin=prepData(bmr, 'country', 'year', TRUE, 
	1999, 2010, TRUE, c('democracy'), TRUE, TRUE)

### FH (ends at 2013)
setwd(paste0(baseData,'/regimeData/Other'))
fh=read.csv('fhdata.csv')
fh$country=char(fh$country)
fh$country[fh$country=='Congo (Kinshasa)']='Democratic Republic of Congo'
fhFin=prepData(fh, 'country', 'year', TRUE,
	1999, 2013, TRUE, c('Status'), TRUE, TRUE)

### Polity (ends at 2013)
pol=read.csv('p4v2013.csv')
pol$country=char(pol$country)
pol$country[pol$country=='UAE']='United Arab Emirates'
pol$country[pol$country=='Congo Kinshasa']='Democratic Republic of Congo'
polFin=prepData(pol, 'country', 'year', TRUE,
	1999, 2013, TRUE, c('polity2'), TRUE, TRUE)
polFin$drop=0
if(polFin['16484',1]=='SERBIA2006'){polFin['16484','drop']=1}
if(polFin['13905',1]=='SUDAN2011'){polFin['13905','drop']=1}
polFin=polFin[which(polFin$drop==0),1:(ncol(polFin)-1)]

### Create democracy label
lapply(list(fhFin,polFin),function(x) FUN=dim(x))
demData=merge(fhFin, polFin[,c(1,5)], by='id')

demData$democ=0
demData$democ[
	which( demData$Status=='F' & 
		   demData$polity2==10 ) ] = 1

### Polity only dem data with different cuts
demData$polGe10=num(demData$polity2==10)
demData$polGe9=num(demData$polity2>=9)
demData$polGe8=num(demData$polity2>=8)
demData$polGe7=num(demData$polity2>=7)
demData$polGe6=num(demData$polity2>=6)
summary(demData)

### Create polity cats
demData$polCat=NA
demData$polCat[demData$polity2>=6]=4
demData$polCat[demData$polity2>=1 & demData$polity2<6]=3
demData$polCat[demData$polity2<=0 & demData$polity2>-6]=2
demData$polCat[demData$polity2<=-6]=1
##### End of Democracy Datasets #####
#############################################

#############################################
##### Start Mon,Mil,Party Datasets #####
### ARD (ends at 2010)
setwd(paste0(baseData,'/regimeData/ARD'))
ard=read.csv('ard.csv')
ard=ard[which(!is.na(ard$cowcode)),]
ard$country=char(ard$country)
ard$country[ard$country=='Yugoslavia, FR (Serbia/Montenegro)']='Serbia'
ardFin=prepData(ard, 'country', 'year', TRUE, 
	1999, 2010, TRUE, c('mon','mil','onep'), TRUE, TRUE)
ardFin$drop=0
if(ardFin['6511',1]=='SERBIA2006'){ardFin['6511','drop']=1}
ardFin=ardFin[which(ardFin$drop==0),1:(ncol(ardFin)-1)]

### GWF (ends at 2010)
setwd(paste0(baseData,'/regimeData/GWF'))
gwf=read.dta('GWF_AllPoliticalRegimes.dta')
gwf$gwf_country=char(gwf$gwf_country)
gwf$gwf_country[gwf$gwf_country=='Luxemburg']='Luxembourg'
gwf$gwf_country[gwf$gwf_country=='UAE']='United Arab Emirates'
gwf$gwf_country[gwf$gwf_country=='Congo/Zaire']='Democratic Republic of Congo'
gwfFin=prepData(gwf, 'gwf_country', 'year', TRUE, 
	1999, 2010, TRUE, c('gwf_monarchy','gwf_military','gwf_party'), 
	TRUE, TRUE)

### Create mon,mil,party labels
lapply(list(ardFin,gwfFin),function(x) FUN=dim(x))
mmpData=merge(gwfFin, ardFin[,c(1,5:7)], by='id')

mmpData$monarchy=0
mmpData$monarchy[
	which( mmpData$gwf_monarchy==1 &
		   mmpData$mon==1 ) ] = 1

mmpData$military=0
mmpData$military[
	which( mmpData$gwf_military==1 &
		   mmpData$mil==1 ) ] = 1

mmpData$party=0
mmpData$party[
	which( mmpData$gwf_party==1 &
		   mmpData$onep==1 ) ] = 1
##### End of Mon,Mil,Party Datasets #####
#############################################

#############################################
##### Examine by-year dist of labels #####
library(doBy)
summaryBy(democ ~ year, data=demData, FUN=mean)
summaryBy(monarchy ~ year, data=mmpData, FUN=mean)
summaryBy(military ~ year, data=mmpData, FUN=mean)
summaryBy(party ~ year, data=mmpData, FUN=mean)
##### End examine #####
#############################################

#############################################
##### Save #####
setwd(paste0(baseData,'/regimeData'))
write.csv( demData[,c('cname','year',
	names(demData)[6:ncol(demData)])], 
	'demData_99-13.csv')
write.csv( mmpData[,c('cname','year',
	'monarchy','military','party')], 
	'mmpData_99-10.csv')
##### Done #####
#############################################