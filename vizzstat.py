#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is vizzstat, a program to analyze netvizz-files.
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
class TsvUnicodeReader(object):
    def __init__(self, f, dialect=csv.excel_tab, encoding="utf-8", **kwargs):
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

def descriptives_users (filename):
	i=0
	nousers=0
	locale=defaultdict(int)
	gender=defaultdict(int)
	likecount=[]
	commentcount=[]
	reader=CsvUnicodeReader(open(filename,"rb"))
	for row in reader:
		if i>=1:
			# only read the first part of the GDF file (the nodes), stop when edges-section begins
			if row[0]=="edgedef>node1 VARCHAR":
				break
			# only process USER nodes, niet posts
			if row[2]=="user":	
				nousers+=1		
				locale[row[6]] +=1
				gender[row[7]] +=1
				likecount.append(int(row[8]))
				commentcount.append(int(row[10]))
	# for the moment ignoring the other values. we could read, e.g., the number of likes to regress gender on it or the like. could be added later.
		i+=1
		
	print "\nThis is your report for the datafile %s. It is assumed to be a GDF file created by Netvizz. \n" %(filename)
	print "- There are {0} users who engaged in any form with the debate".format(nousers)
	print "- Their gender:"
	for k in sorted(gender.iteritems(),key=lambda (k,v):v,reverse=True):
		print k[0]+"\t"+str(k[1])
	print "- Their locale settings:"
	for k in sorted(locale.iteritems(),key=lambda (k,v):v,reverse=True):
		print k[0]+"\t"+str(k[1])
	print "- The number of likes a user made is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(likecount), std(likecount), amin(likecount), amax(likecount), skew(likecount), kurtosis(likecount))
	print "- The number of comments a user made is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(commentcount), std(commentcount), amin(commentcount), amax(commentcount), skew(commentcount), kurtosis(commentcount))

def descriptives_comments (filename):
	isreply=0
	likecount=[]
	reader=TsvUnicodeReader(open(filename,"rb"))
	i=0
	for row in reader:
		if i>=1:
			isreply=isreply+int(row[6])
			likecount.append(int(row[9]))												
		i+=1
	print "\nThis is your report for the datafile %s. It is assumed to be a netvizz-file containing data on facebook-COMMENTS. \n" %(filename)
	print "- In total, there are {0} comments in the dataset. {1} are replies, {2} are not.".format(len(likecount), isreply, len(likecount)-isreply)
	print "- The comments are liked M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(likecount), std(likecount), amin(likecount), amax(likecount), skew(likecount), kurtosis(likecount))
	print "\n"

def descriptives_posts (filename):
	nocomments=[]
	nocommentsbase=[]
	nocommentsreply=[]
	noshares=[]
	nocomment_likes=[]
	noengagement=[]
	nolikes=[]
	photo=0
	video=0
	link=0
	status=0
	reader=TsvUnicodeReader(open(filename,"rb"))
	i=0
	for row in reader:
		if i>=1:
			try:
				nolikes.append(int(row[8]))
			except:
				nolikes.append(0)
			try:
				nocomments.append(int(row[10]))
			except:
				nocomments.append(0)
			try:
				nocommentsbase.append(int(row[11]))
			except:
				nocommentsbase.append(0)
			try:
				nocommentsreply.append(int(row[12]))
			except:
				nocommentsreply.append(0)
			try:
				noshares.append(int(row[13]))
			except:
				noshares.append(0)
			try:
				nocomment_likes.append(int(row[14]))
			except:
				nocomment_likes.append(0)
			try:
				noengagement.append(int(row[15]))
			except:
				noengagement.append(0)
			if row[0]=="video":
				video+=1
			if row[0]=="photo":
				photo+=1
			if row[0]=="status":
				status+=1
			if row[0]=="link":
				link+=1
												
		i+=1
	print "\nThis is your report for the datafile %s. It is assumed to be a netvizz-file containing data on facebook-POSTS. \n" %(filename)
	print "- In total, there are {0} posts in the dataset, containing {1} status updates, {2} links, {3} photos and {4} videos.".format(len(nolikes), status, link, photo, video)
	print "- The posts are liked M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(nolikes), std(nolikes), amin(nolikes), amax(nolikes), skew(nolikes), kurtosis(nolikes))
	print "- The posts have been shared M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(noshares), std(noshares), amin(noshares), amax(noshares), skew(noshares), kurtosis(noshares))
	print "- There are M = {0:.2f} (SD = {1:.2f}) comments on these posts; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(nocomments), std(nocomments), amin(nocomments), amax(nocomments), skew(nocomments), kurtosis(nocomments))
	print "- There are M = {0:.2f} (SD = {1:.2f}) direct comments on these posts; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(nocommentsbase), std(nocommentsbase), amin(nocommentsbase), amax(nocommentsbase), skew(nocommentsbase), kurtosis(nocommentsbase))
# engagement is(users that comment or like the same post are connected
	print "- There are M = {0:.2f} (SD = {1:.2f}) comments which are replies to other comments; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(nocommentsreply), std(nocommentsreply), amin(nocommentsreply), amax(nocommentsreply), skew(nocommentsreply), kurtosis(nocommentsreply))
	print "- The number of aggregated comment likes per post is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(nocomment_likes), std(nocomment_likes), amin(nocomment_likes), amax(nocomment_likes), skew(nocomment_likes), kurtosis(nocomment_likes))
	print "- The enagement (= shares + likes + comments + comment likes) per post is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(mean(noengagement), std(noengagement), amin(noengagement), amax(noengagement), skew(noengagement), kurtosis(noengagement))
	print "\n"


	print "As a table:\n"
	
	print "     \tM\tSD\tmin\tmax\tskew\tkurtosis"
	print "Likes   \t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(nolikes), std(nolikes), amin(nolikes), amax(nolikes), skew(nolikes), kurtosis(nolikes))
	print "Shares   \t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(noshares), std(noshares), amin(noshares), amax(noshares), skew(noshares), kurtosis(noshares))
	print "Comments\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(nocomments), std(nocomments), amin(nocomments), amax(nocomments), skew(nocomments), kurtosis(nocomments))
	print "– direct\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(nocommentsbase), std(nocommentsbase), amin(nocommentsbase), amax(nocommentsbase), skew(nocommentsbase), kurtosis(nocommentsbase))
# engagement is(users that comment or like the same post are connected
	print "– replies\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(nocommentsreply), std(nocommentsreply), amin(nocommentsreply), amax(nocommentsreply), skew(nocommentsreply), kurtosis(nocommentsreply))
	print "ComLikes1\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(nocomment_likes), std(nocomment_likes), amin(nocomment_likes), amax(nocomment_likes), skew(nocomment_likes), kurtosis(nocomment_likes))
	print "Enagement2\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(mean(noengagement), std(noengagement), amin(noengagement), amax(noengagement), skew(noengagement), kurtosis(noengagement))
	print "1 The aggregated number of likes a comment on a post receives"
	print "2 engagement = shares + likes + comments + comment likes" 
	print "\n"
	print "\n"



def content(filename,textcolumn):
	countbestand=filename+"_count.csv"
	print textcolumn
	print type(textcolumn)
	# TODO: LIJST MET STOPWOORDEN DOOR GEBRUIKER LATEN AANLEVEREN
	eruitgooien=[""]

	# how many words to include in word count. For the most often used 10%, write 0.1"
	percentage=0.05
	i=0
	messages_list=[]
	global messages_processed_list
	messages_processed_list=[]
	lengte_list=[]
	print "Opening",filename
	reader=TsvUnicodeReader(open(filename,"r"))
	print "Reading message nr. "
	for row in reader:
		i=i+1
		print "\r",str(i)," ",
		sys.stdout.flush()
		messages_list.append(row[textcolumn])
		lengte_list.append(len(row[textcolumn]))
	print str(i)+" messages, mean length: "+str(mean(lengte_list))+", SD = "+str(std(lengte_list))+", median = "+str(median(lengte_list))
	i=0
	print "Processing message nr. "
	for message in messages_list:
		i=i+1
		print "\r",str(i)," ",
		sys.stdout.flush()	
		for p in list(punctuation):
			message_processed=message.replace(p,' ')
		message_processed = ' '.join([word for word in message_processed.split() if word not in (eruitgooien)])
		# message_processed = ' '.join([word for word in message_processed.split() if len(word)>1])
		# dubbele woorden eruit
		message_processed=' '.join(unique_list(message_processed.split()))	
		messages_processed_list.append(message_processed)	
	wordlist=[]
	for message in messages_processed_list:
		wordlist=wordlist+message.split()
	numberofwords=len(wordlist)
	numberofwordsmostfreq=int(numberofwords*percentage)
	print "\nThere are "+str(numberofwords)+" words in the dataset. We will count the most frequently used "+ str(numberofwordsmostfreq) + "words, which is a fraction of "+str(percentage)+"."
	print "Counting words ..."
	global c
	c=Counter(wordlist)
	print "Write count table to"+countbestand
	with codecs.open(countbestand, "wb", encoding="utf-8", errors="replace") as f:
		for k,v in c.most_common(numberofwordsmostfreq):
			f.write( u"{},{}\n".format(v,k) )



def cooccurrences(filename):
	gdfbestand=filename+"_netwerk.gdf"

	minedgeweight=0

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
	for k in verwijderen:
			del cooc[k]
	f.write("edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE\n")
	for k, v in cooc.iteritems():
		regel= ",".join(k)+","+str(v)
		f.write(regel+"\n")
	print "Done! GDF-file writetn to",gdfbestand

# start main program

print "vizzstat  Copyright (C) 2014  Damian Trilling"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
print "\n"


parser=argparse.ArgumentParser(description='This program creates a report with summary statistics of Facebook data. As input, it takes files created py the "page data" function provided by netvizz (apps.facebook.com/netvizz)')
parser.add_argument("filename", help="The file you want to analyze")
parser.add_argument("filetype", choices=["a","b","c"], help="a b or c - the file type as provided by netvizz: (a) bipartite graph file in gdf format that shows posts, users, and connections between the two; (b) tabular file (tsv) that lists different metrics for each post; (c) tabular file (tsv) that contains the text of user comments.")
parser.add_argument("--descriptives", help="Provides general descriptive statistics", action="store_true")
parser.add_argument("--content", help="Analyzes the content and provides statistics like the average message length or the most frequently used words", action="store_true")
parser.add_argument("--cooccurrences", help="Equal to --content, but in addition, it procudes a GDF-file with word-cooccurrences", action="store_true")



args=parser.parse_args()
if args.descriptives:
	if args.filetype=="a":
		descriptives_users(args.filename)
	if args.filetype=="b":
		descriptives_posts(args.filename)
	if args.filetype=="c":
		descriptives_comments(args.filename)

if args.content:
	if args.filetype=="c":
		content(args.filename,7)
	if args.filetype=="b":
		content(args.filename,2)
	if args.filetype=="a":
		print "-- content is not available for graph files (type a). Please make a different choice. "

if args.cooccurrences:
	if args.filetype=="a":
		print "-- cooccurances is not available for graph files (type a). Please make a different choice. "
	# first call content, it's a prerequisite
	if args.filetype=="c":
		content(args.filename,7)
	if args.filetype=="b":
		content(args.filename,2)
	# now the real work:
	cooccurrences(args.filename)
