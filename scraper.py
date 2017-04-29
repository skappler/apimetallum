#!/usr/bin/env python2

import sys
import os

from api import API
		
def writeLyricsForBand(b, path):
	api = API()
	debug = False
	print "Getting lyrics for Band", b
	id = api.getBandIdByName(b)
	albums = api.getAlbumsByBandId(id)
	for (aid, name) in albums:
		try:
			print "Scraping Album",str(name)
		except:
			print "Scraping non-ASCII album"
		songs = api.getAlbumById(aid)
		for (sid, title) in songs:
			try:
				print "Lyrics for Song",str(title)
			except:
				print "Lyrics for non-ascii Song"
			lyrics = api.getLyricsForSongId(sid)
			if debug:
				print lyrics
			if path:
				with open(path, "a") as f:
					f.write(lyrics.encode("UTF-8"))
			print "\n"
		
def main():
	#response = requests.get("http://www.metal-archives.com/band/discography/id/146/tab/main")
	api = API()

	debug = False
	if len(sys.argv) > 2:
		path = sys.argv[2]
	else:
		path = ""
	
	band = sys.argv[1]
	bands = list()
	if os.path.isfile(band):
		with open(band, "r") as f:
			bands = f.readlines()
	else:
		bands.append(band)
	
	for b in bands:
		if not len(b.strip()) > 0:
			continue
		writeLyricsForBand(b, path)
	
if __name__ == "__main__":
	main()
