#!/usr/bin/env python2

import sys
import os

from api import API
from scraper import writeLyricsForBand

import signal
import traceback
import requests

import ast

crawled = list()
mapping = dict()
ids = list()

def signal_handler(signal, frame):
	print "EXITED"
	with open("save.crwl","w") as f:
		f.write(str(crawled)+"\n")
		print crawled
		f.write(str(ids)+"\n")
		print ids
		f.write(str(mapping)+"\n")
		print mapping
	sys.exit(0)

def main():
	#signal.signal(signal.SIGINT, signal_handler)
	global crawled
	global mapping
	global ids
	api = API()
	api.setDebug(False)
	
	arg1 = sys.argv[1]
	if os.path.isfile(arg1) and ".crwl" in arg1:
		with open(arg1, "r") as f:
			l = f.readlines()
			crawled = ast.literal_eval(l[0])
			ids = ast.literal_eval(l[1])
			mapping = ast.literal_eval(l[2])
	else:
		id = api.getBandIdByName(arg1)
		ids.append(id)
		mapping[id] = arg1
	
		
	
	if len(sys.argv) > 2:
		path = sys.argv[2]
	else:
		path = ""
	
	try:
		while ids:
			i = ids[0]
			try:
				genre = api.getGenreForBandId(i)
			except requests.exceptions.RequestException as e:
				continue
			if not "Black" in genre:
			#if not "Black Metal" in genre:
				ids.pop(0)
				crawled.append(i)
				print "Skipping", mapping[i], "as it is a",genre,"band"
				continue
			print "Found", mapping[i]
			if path:
				writeLyricsForBand(mapping[i].encode("UTF-8"), path)
				#with open(path, "a") as f:
				#	f.write(mapping[i].encode("UTF-8")+"\n")
			try:
				rec = api.getRecommendationsForId(i)
			except requests.exceptions.RequestException as e:
				continue
			for (aid, name) in rec:
				if not aid in crawled and not aid in ids:
					mapping[aid] = name
					try:
						str(name)
						ids.append(aid)
					except:
						crawled.append(aid)
						#	ids.pop()
						print "skipped", aid, "because it's not ascii"
			crawled.append(i)
			ids.pop(0)	
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		print ''.join('!! ' + line for line in lines) 
		signal_handler(None,None)	
		
if __name__ == "__main__":
	main()
