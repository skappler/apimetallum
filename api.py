import requests
import bs4
import sys
import os
import urllib

class API:
	
	def __init__(self):
		self.baseUrl = "http://www.metal-archives.com/"
		self.debug = True
		self.crawlSize = 5
		
	def setDebug(self, debug):
		self.debug = debug
		
	def setCrawlSize(self, size):
		self.crawlSize = size
		
	def getBandIdByName(self, name):
		name = name.replace(" ","_")
		if self.debug:
			print "GET", self.baseUrl+"bands/"+name
			
		response = requests.get(self.baseUrl+"bands/"+urllib.quote_plus(name))
		if "Band not found" in response.text:
			return -1
		try:
			id = [l for l in response.text.split("\n") if "bandId" in l][0].split(" = ")[1][:-1]
			return int(id)
		except:
			#multiple bands with name
			soup = bs4.BeautifulSoup(response.text)
			return int(soup.select("h1 ~ ul li a")[0].attrs.get("href").split("/")[-1])
	
	def getGenreForBandId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"bands/_/"+str(id)
			
		response = requests.get(self.baseUrl+"bands/_/"+str(id))
		soup = bs4.BeautifulSoup(response.text)
		return soup.select("dl.float_right dd")[0].getText()

	
	def getRecommendationsForId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"band/ajax-recommendations/id/"+str(id)
		response = requests.get(self.baseUrl+"band/ajax-recommendations/id/"+str(id))
		soup = bs4.BeautifulSoup(response.text)
		
		return [(int(x.attrs.get("href").split("/")[-1]),x.getText()) for x in soup.select("tbody tr td a")[:self.crawlSize]]
	
	def getAlbumsByBandId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"band/discography/id/%s/tab/main" % str(id)
			
		response = requests.get(self.baseUrl+"band/discography/id/%s/tab/main" % str(id))
		ret = list()
		soup = bs4.BeautifulSoup(response.text)
		links = soup.select("a[href*=albums]")
		for a in links:
			ret.append((int(a.attrs.get("href").split("/")[-1]), unicode(a.getText())))
		return ret
	
	def getAlbumById(self, id):
		if self.debug:
			print "GET", self.baseUrl + "albums/_/_/%s" % str(id)
			
		response = requests.get(self.baseUrl + "albums/_/_/%s" % str(id))	
		soup = bs4.BeautifulSoup(response.text)
		links = soup.select("tr.odd")
		links.extend(soup.select("tr.even"))
		ret = list()
		for col in links:
			sids = col.select("a.anchor")
			stitles = col.select("td.wrapWords")
			if not sids or not stitles:
				continue
			sid = sids[0].attrs.get("name").strip()
			stitle = stitles[0].getText().strip()
			ret.append((sid,stitle))
		return ret
		
	def getLyricsForSongId(self, id):
		if self.debug:
			print "GET", self.baseUrl + "release/ajax-view-lyrics/id/"+ str(id)
		response = requests.get(self.baseUrl + "release/ajax-view-lyrics/id/"+ str(id))
		lyrics = unicode(response.text.replace("<br />","").strip())
		if "(lyrics not available)" in lyrics or "Instrumental" in lyrics:
			return ""
		try:
			str(lyrics)
			return lyrics
		except:
			if self.debug:
				print "Skipping because lyrics are non ASCII"
			return ""
