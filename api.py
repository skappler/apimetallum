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

	def __soup(self, target):
		return bs4.BeautifulSoup(target.text, "lxml")
		
	def setDebug(self, debug):
		self.debug = debug
		
	def setCrawlSize(self, size):
		self.crawlSize = size
		
	def getBandIdByName(self, name):
		return self.getAllBandIdsByName(name)[0]

	def getAllBandIdsByName(self, name):
		name = name.replace(" ", "_")
		if self.debug:
			print "GET", self.baseUrl + "bands/" + name

		response = requests.get(self.baseUrl + "bands/" + name)
		if "Band not found" in response.text:
			return [-1]
		try:
			id = [l for l in response.text.split("\n") if "bandId" in l][0].split(" = ")[1][:-1]
			return [int(id)]
		except:
			# multiple bands with name
			soup = self.__soup(response)

			return [int(x.attrs.get("href").split("/")[-1]) for x in soup.select("h1 ~ ul li a")]
	
	def getGenreForBandId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"bands/_/"+str(id)
			
		response = requests.get(self.baseUrl+"bands/_/"+str(id))
		soup = self.__soup(response)
		return soup.select("dl.float_right dd")[0].getText()


	def getOriginForBandId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"bands/_/"+str(id)

		response = requests.get(self.baseUrl+"bands/_/"+str(id))
		soup = self.__soup(response)
		return soup.select("dl.float_left dd a")[0].getText()

	
	def getRecommendationsForId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"band/ajax-recommendations/id/"+str(id)
		response = requests.get(self.baseUrl+"band/ajax-recommendations/id/"+str(id))
		soup = self.__soup(response)
		if len(soup.select('#no_artists')) > 0:
			# This band has no recommendations
			return []
		table = [x.find_all('td') for x in soup.select("tbody tr")[:self.crawlSize]]
		def parseRow(row):
			link = row[0].a
			origin = row[1].getText()
			genre = row[2].getText()
			return int(link.attrs.get("href").split("/")[-1]), link.getText().encode(response.encoding), origin, genre
		return map(parseRow, table)
	
	def getAlbumsByBandId(self, id):
		if self.debug:
			print "GET", self.baseUrl+"band/discography/id/%s/tab/main" % str(id)
			
		response = requests.get(self.baseUrl+"band/discography/id/%s/tab/main" % str(id))
		ret = list()
		soup = self.__soup(response)
		links = soup.select("a[href*=albums]")
		for a in links:
			ret.append((int(a.attrs.get("href").split("/")[-1]), a.getText().encode(response.encoding)))
		return ret
	
	def getAlbumById(self, id):
		if self.debug:
			print "GET", self.baseUrl + "albums/_/_/%s" % str(id)
			
		response = requests.get(self.baseUrl + "albums/_/_/%s" % str(id))	
		soup = self.__soup(response)
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
