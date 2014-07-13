# Scraper for  Religious Freedom: 2001-July/December 2010

import time
import os
from compiler.ast import flatten
import json

# My helper functions
os.chdir('/Users/janus829/Desktop/Research/WardProjects/regimeClassif/Scrapers')
from helpers import *

# Data storage
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Data')

# State Dept Religious Freedom reports aggregate website
address = 'http://www.state.gov/j/drl/irf/rpt/index.htm'

# Find links to various years
yrURLs=subLinks(address, 'div', 'id', "tier3-local-nav", 
	'title', 'href="', '">')
yrURLs=yrURLs[2:len(yrURLs)-2] # Format of human rights site changes substantially after 2009
yrURLs.reverse()

# Run through years
for address in yrURLs:
	print 'Collecting data from ' + address +'\n'

	# Find links to regions
	regURLs=subLinks(address, 'div', 'id', 'tier3-local-nav',
		'<a title=', 'href="', '">')

	# Get country links for region-year
	ctryYrData=[]
	for region in regURLs:
		urls=subLinks(region, 'div', 'id', 'tier3-landing-content-wide',
			'<a target="_self" ', 'href="', '">', 
			labels=True, lc1='.htm">', lc2='</a>')		
		ctryYrData.append(urls)
	ctryYrData=flatten(ctryYrData)

	# Add Data
	for ctry in ctryYrData:
		ctry['source']='StateRF'
		ctry['year']=cleanStrSoup(address, 'irf/','/index')
		ctry['data']=getText(ctry['url'], 'div', 'id', 'centerblock')
		time.sleep(2)
		print '   ...data for ' + ctry['name'] + ' collected'

	# Save to json
	print '\n Data for ' + ctry['year'] + ' collected \n'	
	filename=ctry['source'] + '_' + ctry['year'] + '.json'
	f=open(filename, 'wb')
	json.dump(ctryYrData, f, sort_keys=True)
	f.close()