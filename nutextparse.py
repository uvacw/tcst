#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from io import open


from lxml import html
import urllib2  


from os import listdir
from os.path import isfile, join

import argparse

print "NuTextParse 0.1 Copyright (C) 2014  Damian Trilling"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
print "\n"


def parsetext(htmlstring):
	tree = html.fromstring(htmlstring)
	titel=tree.xpath('//*[@id="leadarticle"]/div[1]/h1/text()')
	gepubliceerd=tree.xpath('//*[@id="leadarticle"]/div[1]/div/div[1]/div[2]/text()')
	tekst=tree.xpath('//*[@id="leadarticle"]/div[2]//*/text()')
	#print tekst
	return (titel,gepubliceerd,tekst)





parser=argparse.ArgumentParser(description='This program parses the top 5 most read articles from nu.nl. As input, it takes either a folder of saved nu.nl-homepages or it looks up the top 5 at this moment.')
parser.add_argument("folder", nargs="?", help="In which folder are the saved nu.nl-homepages")
parser.add_argument("--live", help="NOT IMPLEMENTED", action="store_true")

args=parser.parse_args()

if args.live:
	req=urllib2.Request("http://www.nu.nl/buitenland/3824727/duitsland-draagt-cia-gezant-land-verlaten.html")
	htmlstring=urllib2.urlopen(req).read()
	tekst=parsetext(htmlstring)
	with open ("output.txt", mode="w", encoding="utf-8") as fo:
		 fo.write(unicode(tekst[0][0])+"\n\n")
		 fo.write("Published: "+unicode(tekst[1][0])+"\n")
		 fo.write("Updated: "+unicode(tekst[1][1])+"\n\n")
		 for line in tekst[2]:
			 fo.write(unicode(line))
	print "Saved to output.txt"

elif args.folder:
	mypath=args.folder
	print "Analyzing files stored in",mypath
	onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]		
	for filename in onlyfiles:
		with open(mypath+filename,mode="r", encoding="utf-8") as f:
			htmlstring=f.read()
			tekst=parsetext(htmlstring)
			#print tekst
			with open (mypath+filename+"_stripped.txt", mode="w", encoding="utf-8") as fo:
				try:
					fo.write(unicode(tekst[0][0])+"\n\n")
					fo.write("Published: "+unicode(tekst[1][0])+"\n")
					fo.write("Updated: "+unicode(tekst[1][1])+"\n\n")
					#print len(tekst[2])
					for line in tekst[2]:
						fo.write(unicode(line))
				except:
					print "ERROR PROCESSING",filename
else:
	print "Specify either a folder name or --live"

