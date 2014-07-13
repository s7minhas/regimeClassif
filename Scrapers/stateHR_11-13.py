# Scraper for Human Rights Reports from 2011-2013

import time
import os
from compiler.ast import flatten
import json

# My helper functions
os.chdir('/Users/janus829/Desktop/Research/WardProjects/regimeClassif/Scrapers')
from helpers import *

# Data storage
os.chdir('/Users/janus829/Dropbox/Research/WardProjects/regimeClassif/Data')

# Building Web Address for State Department Reports
base = 'http://www.state.gov/j/drl/rls/hrrpt/'
yrURLs = [base+x+'humanrightsreport' for x in ['2011','2012','']]

# Run through years
for addressYr in yrURLs:
	year=2011
	print 'Collecting data from ' + addressYr +'\n'	

	# Pull out links for countries
	ctryYrData=subLinks(addressYr, 'div', 'id', 'countries', 
			'<li>', '<a href="', '" title=',
			True, 'title="', '" target="')

	# Scrape info
	for ctry in ctryYrData:

		# load webpage
		ctry['source']='StateHR'
		ctry['year']=str(year)
		ctry['data']=getText(ctry['url'], 'div', 'id', 'centerblock')
		time.sleep(3)
		print '   ...data for ' + ctry['name'] + ' collected'		

	# Save to json
	year+=1
	print '\n Data for ' + ctry['year'] + ' collected \n'	
	filename=ctry['source'] + '_' + ctry['year'] + '.json'
	f=open(filename, 'wb')
	json.dump(ctryYrData, f, sort_keys=True)
	f.close()