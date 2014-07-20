import urllib2
from BeautifulSoup import BeautifulSoup as bsoup
import re
import time

def openSoup(x):
	"""Opens URL and create soup"""
	try:
		return bsoup(urllib2.urlopen(x).read())
	except urllib2.HTTPError, e:
		print 'Taking a breather...'
		time.sleep(120)
		return bsoup(urllib2.urlopen(x).read())

def cleanStrSoup(x, a, b, adj=None):
	"""Returns the text between strings a and b"""
	if adj is None: 
		adj=len(a)
	return x[x.find(a)+adj:x.find(b)]

def subLinks(link, s1, s2, s3, spl, c1, c2, labels=False, lc1='', lc2=''):
	discards=['tier3-local-nav', 'tier3-landing-content-wide', 'Preface',
	 'Front Matter', 'Appendices', 'Related Material', 'format as a single',
	 '/documents/organization/']
	URLs=[]	
	soup = openSoup(link)
	dirt=soup(s1, {s2:s3})
	dirt=str(dirt).split(spl)
	for d in dirt:
		if not any(x for x in discards if x in d):	
			if 'href' in d:
				if labels:
					URLs.append( { 'name':cleanStrSoup(d, lc1, lc2), 
						'url':cleanStrSoup(d, c1, c2) } )
				else: 
					URLs.append( cleanStrSoup(d, c1, c2)  )
	return URLs

def cleanHTML(html):
  cleaner = re.compile('<.*?>')
  cleanTxt = re.sub(cleaner,'', html)
  return cleanTxt

def getText(link, s1, s2, s3):
	dirt=openSoup(link)
	data=dirt(s1, {s2:s3})
	text=cleanHTML( str(data) )
	return text

def dedupeLoD(x, dictID):
	y=[]
	seen=[]
	for i in x:
		if i[dictID] not in seen:
			y.append(i)
			seen.append(i[dictID])
	return y	