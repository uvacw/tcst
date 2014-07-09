#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from io import open


import csv

from lxml import html
import urllib2  
from unicsv import CsvUnicodeWriter

import datetime

from os import listdir
from os.path import isfile, join

import argparse

print "NUtop5 0.1 Copyright (C) 2014  Damian Trilling"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
print "\n"

outputfilename="output.csv"



def parsetopfive(htmlstring):
	try:
		tree = html.fromstring(htmlstring)
	except:
		return(['ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING'],['ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING'],['ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING','ERROR WHILE PARSING'])
	
	meestgelezen_positie=tree.xpath('//*[@id="rightcolumn"]/div[6]/div/div[1]/ul/li[*]/@data-vr-contentbox')
	meestgelezen_links=tree.xpath('//*[@id="rightcolumn"]/div[6]/div/div[1]/ul/li[*]/a/@href')
	meestgelezen_titles=tree.xpath('//*[@id="rightcolumn"]/div[6]/div/div[1]/ul/li[*]/a/@title')
	
	if not meestgelezen_positie:		# workaround voor ouder layout
		meestgelezen_positie=tree.xpath('//*[@id="rightcolumn"]/div[7]/div/div[1]/ul/li[*]/@data-vr-contentbox')
		meestgelezen_links=tree.xpath('//*[@id="rightcolumn"]/div[7]/div/div[1]/ul/li[*]/a/@href')
		meestgelezen_titles=tree.xpath('//*[@id="rightcolumn"]/div[7]/div/div[1]/ul/li[*]/a/@title')
	
	
	return (meestgelezen_positie,meestgelezen_links,meestgelezen_titles)




parser=argparse.ArgumentParser(description='This program parses the top 5 most read articles from nu.nl. As input, it takes either a folder of saved nu.nl-homepages or it looks up the top 5 at this moment.')
parser.add_argument("folder", nargs="?", help="In which folder are the saved nu.nl-homepages")
parser.add_argument("--live", help="Look at the top 5 right now instead of analyzing saved homepages", action="store_true")

args=parser.parse_args()

if args.live:
	req=urllib2.Request("http://www.nu.nl")
	htmlstring=urllib2.urlopen(req).read()
	t5=parsetopfive(htmlstring)
	bron=unicode(datetime.datetime.now())
	with open(outputfilename,"wb") as fo:     #belangrijk, als Binary openen (vanwege csv-module=
		outputwriter=csv.writer(fo, delimiter=b";", quotechar=b'"', quoting=csv.QUOTE_MINIMAL)
		for i in range(5):
			row=[bron,unicode(t5[0][i]),unicode("http://www.nu.nl"+t5[1][i]),unicode(t5[2][i])]
			outputwriter.writerow([s.encode("utf-8") for s in row])

elif args.folder:
	mypath=args.folder
	print "Analyzing files stored in",mypath
	onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

	with open(outputfilename,"wb") as fo:     #belangrijk, als Binary openen (vanwege csv-module)
		outputwriter=csv.writer(fo, delimiter=b";", quotechar=b'"', quoting=csv.QUOTE_MINIMAL)
		for filename in onlyfiles:
			bron=filename
			with open(mypath+filename,mode="r", encoding="utf-8") as f:
				htmlstring=f.read()
				t5=parsetopfive(htmlstring)
				for i in range(5):
					try:
						row=[bron,unicode(t5[0][i]),unicode("http://www.nu.nl"+t5[1][i]),unicode(t5[2][i])]
					except:
						row=[bron,"ERROR","ERROR","ERROR"]
					outputwriter.writerow([s.encode("utf-8") for s in row])
			
else:
	print "Specify either a folder name or --live"

