# Helpful libaries and functions
source('~/Research/WardProjects/regimeClassif/Analysis/Supervised/setup.R')

# Set up plot space
xDim=c(0,10); yDim=c(0,10); n=15

# Margins
slope=-.8; ints=c(10, 9, 11)

# Generate points
getY=function(x,int,m){ int + m * x }
xA=round(runif(n, xDim[1], xDim[2]), 2); yA=runif(n, xDim[1], getY(xA, ints[2], slope)-.1)
xB=round(runif(n, xDim[1], xDim[2]), 2); yB=runif(n, getY(xB, ints[3], slope)+.05, xDim[2]+.3)

# Plot
ggData=data.frame( rbind( cbind(xA, yA), cbind(xB, yB) ))
ggData$class=rep(c('A', 'B'), each=n)
lineData=data.frame(cbind(ints, slope))

tmp=ggplot()+geom_point(data=ggData, aes(x=xA, y=yA, pch=class, color=class), size=4)
tmp=tmp+geom_abline(data=lineData, aes(intercept=ints, slope=slope), linetype=c(1,2,2))
tmp=tmp+theme(
	legend.position='none',
	axis.text=element_blank(), axis.ticks=element_blank(), axis.title=element_blank(),
	panel.grid.major=element_blank(), panel.grid.minor=element_blank()
	)
makePlot(tmp, 'svmIntro')