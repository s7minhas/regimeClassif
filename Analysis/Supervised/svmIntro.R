# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

# Set up plot space
xDim=c(0,10); yDim=c(0,10); n=15

# Margins
slope=-.8; ints=c(10, 9, 11)

# Generate points and margins
getY=function(x,int,m){ int + m * x }
xA=round(runif(n, xDim[1], xDim[2]), 2); yA=runif(n, xDim[1], getY(xA, ints[2], slope)-.1)
xB=round(runif(n, xDim[1], xDim[2]), 2); yB=runif(n, getY(xB, ints[3], slope)+.05, xDim[2]+.3)
ggData=data.frame( rbind( cbind(xA, yA), cbind(xB, yB) ))
ggData$class=rep(c('A', 'B'), each=n)
lineData=data.frame(cbind(ints, slope))

# Support vectors
suppA=c(2.5, 5.0, 8)
suppB=c(3.75, 7, 9)
suppData=data.frame(rbind(
	cbind(xS=suppA, yS=getY(suppA, ints[2], slope),cS='A'),
	cbind(suppB, getY(suppB, ints[3], slope), 'B')) )
suppData=convNumDcol(suppData, c('xS', 'yS'))

# Plot
tmp=ggplot()+geom_point(data=ggData, aes(x=xA, y=yA, pch=class, color=class), size=4, alpha=.6)
tmp=tmp+geom_abline(data=lineData, aes(intercept=ints, slope=slope), linetype=c(1,2,2))
tmp=tmp+geom_point(data=suppData, aes(x=xS, y=yS, pch=cS, color=cS), size=4)
tmp=tmp+theme(
	legend.position='none',
	axis.text=element_blank(), axis.ticks=element_blank(), axis.title=element_blank(),
	panel.grid.major=element_blank(), panel.grid.minor=element_blank()
	)
makePlot(tmp, 'svmIntro', hgt=2, wdh=4, pdf=TRUE, tex=FALSE)