# Scraper for Freedom House: 1999-2014

import time
import os
from compiler.ast import flatten
import json

# My helper functions
os.chdir('/Users/janus829/Desktop/Research/WardProjects/regimeClassif/Scrapers')
from helpers import *

# Data storage
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Data')

# Yearly web addresses (no data for 2000)
base='http://freedomhouse.org/report/freedom-world/freedom-world-'
yrURLs=[base+str(x) for x in flatten([1998,1999,range(2001,2015,1)])]

# Run through years
for addressYr in yrURLs:
	print 'Collecting data from ' + addressYr +'\n'	

	# Pull out links for countries
	ctryYrData=subLinks(addressYr, 'span', 'class', 'field-content', 
		'<span class="field-content">', '<a href="', '">',
		True, '">', '</a></span>')
	ctryYrData=dedupeLoD(ctryYrData, 'name')

	# Set first country link to Afghanistan
	# (leads to exclusion of Abkhazia in 1998 and 2002-2013)
	names=[x['name'] for x in ctryYrData]
	ctryYrData = ctryYrData[names.index('Afghanistan'):len(ctryYrData)]

	# Scrape info
	for ctry in ctryYrData:

		# load webpage
		address='http://freedomhouse.org'+ctry['url']
		ctry['source']='FH'
		ctry['year']= addressYr[len(addressYr)-4:len(addressYr)]
		ctry['data']=getText(address, 'div', 'class', 'group-left')
		time.sleep(3)
		print '   ...data for ' + ctry['name'] + ' collected'		

	# Save to JSON
	print '\n Data for ' + ctry['year'] + ' collected \n'	
	filename=ctry['source'] + '_' + ctry['year'] + '.json'
	f=open(filename, 'wb')
	json.dump(ctryYrData, f, sort_keys=True)
	f.close()