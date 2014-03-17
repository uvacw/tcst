#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is csv2gdf, a program to create GDF network files based on CSV input files.
# Copyright (C) 2014 DAMIAN TRILLING
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact me via d dot c dot trilling at uva dot nl


from __future__ import division
import codecs, csv, cStringIO
import sys
from numpy import mean, std, amin, amax, median
from collections import Counter
from scipy.stats import skew, kurtosis
from collections import defaultdict
import argparse
from string import punctuation
from itertools import combinations
import re 

class UTF8Recoder(object):
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")
class CsvUnicodeReader(object):
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)
    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self



def unique_list(l):
	ulist = []
	[ulist.append(x) for x in l if x not in ulist]
	return ulist



def countwords(filename,textcolumn,threshold,stopwordfile):
	#countbestand=filename+"_count.csv"
	countbestand="count.csv"
	print stopwordfile
	if stopwordfile=="NULL":
		eruitgooien=[]
	else:
		eruitgooien = [line.strip() for line in open(stopwordfile)]
	percentage=1-threshold
	i=0
	messages_list=[]
	global messages_processed_list
	messages_processed_list=[]
	print "Opening",filename
	reader=CsvUnicodeReader(filename)
	print "Reading row nr. "
	for row in reader:
		i=i+1
		print "\r",str(i)," ",
		sys.stdout.flush()
		messages_list.append(row[textcolumn])
		
	i=0
	print "Processing message nr. "
	for message in messages_list:
		i=i+1
		print "\r",str(i)," ",
		sys.stdout.flush()	
		for p in list(punctuation):
			message_processed=message.replace(p,' ')
		message_processed = ' '.join([word for word in message_processed.split() if word not in (eruitgooien)])
		# dubbele woorden eruit
		message_processed=' '.join(unique_list(message_processed.split()))	
		messages_processed_list.append(message_processed)	
	wordlist=[]
	for message in messages_processed_list:
		wordlist=wordlist+message.split()
	numberofwords=len(wordlist)
	numberofwordsmostfreq=int(numberofwords*percentage)
	print "\nThere are "+str(numberofwords)+" words in the dataset. We will count the most frequently used "+ str(numberofwordsmostfreq) + "words, which is a fraction of "+str(percentage*100)+" per cent."
	print "Counting words ..."
	global c
	c=Counter(wordlist)
	print "Write count table to"+countbestand
	with codecs.open(countbestand, "wb", encoding="utf-8", errors="replace") as f:
		for k,v in c.most_common(numberofwordsmostfreq):
			f.write( u"{},{}\n".format(v,k) )



def cooccurrences(filename,minedgeweight):
	gdfbestand="cooc-netwerk.gdf"

	cooc=defaultdict(int)
	tweets=[]
	
	f = codecs.open(gdfbestand, 'wb', encoding="utf-8")
	for message in messages_processed_list:
		words=message.split()
		for a,b in combinations(words,2):
			if a!=b:
				cooc[(a,b)]+=1
	f.write("nodedef>name VARCHAR, width DOUBLE\n")
	algenoemd=[]
	verwijderen=[]
	for k in cooc:
		if cooc[k]<minedgeweight:
					verwijderen.append(k)
		else:
			if k[0] not in algenoemd:
				f.write(k[0]+","+str(c[k[0]])+"\n")
				algenoemd.append(k[0])
			if k[1] not in algenoemd:
				f.write(k[1]+","+str(c[k[1]])+"\n")
				algenoemd.append(k[1])
	if len(verwijderen)>0:
		print len(verwijderen),"compinations removed because they occur less than",minedgeweight,"times."
	for k in verwijderen:
			del cooc[k]
	f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
	for k, v in cooc.iteritems():
		regel= ",".join(k)+","+str(v)
		f.write(regel+"\n")
	print "\nDone! GDF-file written to ",gdfbestand



def mentions(type,filename,textcolumn,sendercolumn):
	if type=="all":
		gdfbestand="allinteractions-netwerk.gdf"
		zoekstring=re.compile('@([A-Za-z0-9_]+)')
	if type=="rt":
		gdfbestand="rt-netwerk.gdf"
		zoekstring=re.compile('RT.@([A-Za-z0-9_]+)')
	if type=="reply":
		gdfbestand="reply-netwerk.gdf"
		zoekstring=re.compile('^\.?@([A-Za-z0-9_]+)')
	
	# misschien ook deze string: r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+'
	i=0
	# print "Opening",filename
	reader=CsvUnicodeReader(filename)
	print "Reading row nr. "
	edges=defaultdict(int)
	for row in reader:
		i+=1
		print "\r",str(i)," ",
		sys.stdout.flush()
		matches=zoekstring.findall(row[textcolumn])
		for match in matches:
			edges[(row[sendercolumn],match)]+=1
	f = codecs.open(gdfbestand, 'wb', encoding="utf-8")	
	f.write("nodedef>name VARCHAR\n")
	algenoemd=[]
	for k in edges:
		if k[0] not in algenoemd:
			f.write(k[0]+"\n")
			algenoemd.append(k[0])
	f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
	for k, v in edges.iteritems():
		regel= ",".join(k)+","+str(v)
		f.write(regel+"\n")
	print "\nDone! GDF-file written to ",gdfbestand


# start main program

print "csv2gdf  Copyright (C) 2014  Damian Trilling"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
print "\n"
print "Type csv2gdf --help to learn how to use this program."
print "\n"


parser=argparse.ArgumentParser(description='This program creates GDF network files based on input data in CSV format.')
# parser.add_argument("filename", help="The file you want to analyze")
parser.add_argument('filename', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="The file you want to analyze. If you don't provide a filename, we'll read from STDIN")
parser.add_argument("--column", type=int,default=0, help="In which column of the CSV file is the data you want to analyse. We start counting with 0, so the second column is called 1. If not provided, we use column 0.")
parser.add_argument("--sendercolumn", type=int,default=2, help="In which column of the CSV file is the SENDER (only for mention and retweet networks). We start counting with 0, so the second column is called 1. If not provided, we use column 2.")

parser.add_argument("--cutoff", default=0, help="Define a cutoff percentage: The least frequently used x procent are not included. Write 0.1 for 10 per cent. If not provided, we use 0 and thus include all elements.") 
parser.add_argument("--minedgeweight", type=int, default=0, help="Define a minimum edgeweight and discard less frequent coooccurrences.") 
parser.add_argument("--stopwordfile", nargs=1, default=["NULL"], help="A file with stopwords (i.e., words you want to ignore)")
parser.add_argument("--retweet", help="Produces a retweet network", action="store_true")
#parser.add_argument("--mentions", help="Produces a mention network", action="store_true")
parser.add_argument("--reply", help="Produces a mention network", action="store_true")
parser.add_argument("--allinteractions", help="Produces a network that does not distinguish between RT, mention, Reply", action="store_true")
parser.add_argument("--cooccurrences", help="Procudes a GDF-file with word-cooccurrences", action="store_true")



args=parser.parse_args()


if args.retweet:
	mentions("rt",args.filename,int(args.column),int(args.sendercolumn))
if args.allinteractions:
	mentions("all",args.filename,int(args.column),int(args.sendercolumn))
if args.reply:
	mentions("reply",args.filename,int(args.column),int(args.sendercolumn))	
if args.cooccurrences:
	countwords(args.filename, int(args.column),float(args.cutoff),args.stopwordfile[0])
	cooccurrences(args.filename,int(args.minedgeweight))

if (args.retweet or args.allinteractions or args.reply or args.cooccurrences)==False:
	print "You have to select at least one network you want to produce by using one of the following options:"
	print " --retweet  --reply  --allinteractions  --cooccurrences"


