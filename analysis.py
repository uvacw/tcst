#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import division
import codecs, cStringIO
import sys
import re
from unicsv import TsvUnicodeReader, CsvUnicodeReader
import numpy
from collections import Counter
from scipy.stats import skew, kurtosis
from collections import defaultdict


# geef hier de namen van de bestanden aan

# facebookdatabestand="Pietitie niet anoniem page_592411374140027_2014_01_15_15_07_19461acb511ca1b3ca8b6669d423cfdf_comments.tab"
#resultatenbestand="pietitie_comments_cleaned.txt"
#countbestand="pietitie_comments_wordcount.csv"

#facebookdatabestand="Zwarte piet is racisme niet anoniem page_296568710371104_2014_01_15_16_03_6b6ad21276e9e0fadd319eb9390835ba_comments.tab"
#resultatenbestand="zpir_comments_cleaned.txt"
#countbestand="zpir_comments_wordcount.csv"

eruitgooien=["vor","piet","sint","youtube","ok","wel","http","facebook","http","ww","www"]


# how many words to include in word count. For the most often used 10%, write 0.1"
percentage=0.05

# hoe lang moeten berichten zijn om meegenomen te worden?
minimumlengte=10  #tekens

i=0
messages_list=[]
messages_processed_list=[]
#message_lengte=0
lengte_list=[]





# define a number of functions to analyze netvizz-output

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
	print "- The number of likes a user made is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(likecount), numpy.std(likecount), numpy.amin(likecount), numpy.amax(likecount), skew(likecount), kurtosis(likecount))
	print "- The number of comments a user made is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(commentcount), numpy.std(commentcount), numpy.amin(commentcount), numpy.amax(commentcount), skew(commentcount), kurtosis(commentcount))
	
	#for (v,k) in locale:
	#	print v,k	
	#for (v,k) in gender:
	#	print v,k
	
	
	


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
	print "- The comments are liked M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(likecount), numpy.std(likecount), numpy.amin(likecount), numpy.amax(likecount), skew(likecount), kurtosis(likecount))
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
	print "- The posts are liked M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(nolikes), numpy.std(nolikes), numpy.amin(nolikes), numpy.amax(nolikes), skew(nolikes), kurtosis(nolikes))
	print "- The posts have been shared M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(noshares), numpy.std(noshares), numpy.amin(noshares), numpy.amax(noshares), skew(noshares), kurtosis(noshares))
	print "- There are M = {0:.2f} (SD = {1:.2f}) comments on these posts; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(nocomments), numpy.std(nocomments), numpy.amin(nocomments), numpy.amax(nocomments), skew(nocomments), kurtosis(nocomments))
	print "- There are M = {0:.2f} (SD = {1:.2f}) direct comments on these posts; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(nocommentsbase), numpy.std(nocommentsbase), numpy.amin(nocommentsbase), numpy.amax(nocommentsbase), skew(nocommentsbase), kurtosis(nocommentsbase))
# engagement is(users that comment or like the same post are connected
	print "- There are M = {0:.2f} (SD = {1:.2f}) comments which are replies to other comments; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(nocommentsreply), numpy.std(nocommentsreply), numpy.amin(nocommentsreply), numpy.amax(nocommentsreply), skew(nocommentsreply), kurtosis(nocommentsreply))
	print "- The number of aggregated comment likes per post is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(nocomment_likes), numpy.std(nocomment_likes), numpy.amin(nocomment_likes), numpy.amax(nocomment_likes), skew(nocomment_likes), kurtosis(nocomment_likes))
	print "- The enagement (= shares + likes + comments + comment likes) per post is M = {0:.2f} (SD = {1:.2f}) times; min = {2}, max = {3}; skewnewss = {4:.2f}, kurtosis = {5:.2f}".format(numpy.mean(noengagement), numpy.std(noengagement), numpy.amin(noengagement), numpy.amax(noengagement), skew(noengagement), kurtosis(noengagement))
	print "\n"


	print "As a table:\n"
	
	print "     \tM\tSD\tmin\tmax\tskew\tkurtosis"
	print "Likes   \t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(nolikes), numpy.std(nolikes), numpy.amin(nolikes), numpy.amax(nolikes), skew(nolikes), kurtosis(nolikes))
	print "Shares   \t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(noshares), numpy.std(noshares), numpy.amin(noshares), numpy.amax(noshares), skew(noshares), kurtosis(noshares))
	print "Comments\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(nocomments), numpy.std(nocomments), numpy.amin(nocomments), numpy.amax(nocomments), skew(nocomments), kurtosis(nocomments))
	print "– direct\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(nocommentsbase), numpy.std(nocommentsbase), numpy.amin(nocommentsbase), numpy.amax(nocommentsbase), skew(nocommentsbase), kurtosis(nocommentsbase))
# engagement is(users that comment or like the same post are connected
	print "– replies\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(nocommentsreply), numpy.std(nocommentsreply), numpy.amin(nocommentsreply), numpy.amax(nocommentsreply), skew(nocommentsreply), kurtosis(nocommentsreply))
	print "ComLikes1\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(nocomment_likes), numpy.std(nocomment_likes), numpy.amin(nocomment_likes), numpy.amax(nocomment_likes), skew(nocomment_likes), kurtosis(nocomment_likes))
	print "Enagement2\t{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4:.2f}\t{5:.2f}".format(numpy.mean(noengagement), numpy.std(noengagement), numpy.amin(noengagement), numpy.amax(noengagement), skew(noengagement), kurtosis(noengagement))
	print "1 The aggregated number of likes a comment on a post receives"
	print "2 engagement = shares + likes + comments + comment likes" 
	print "\n"
	print "\n"


# start main program

# first of all, let's have a look at the general 
descriptives_posts ("data/Pietitie niet anoniem page_592411374140027_2014_01_15_15_07_19461acb511ca1b3ca8b6669d423cfdf.tab")
descriptives_posts("data/Zwarte piet is racisme niet anoniem page_296568710371104_2014_01_15_16_03_6b6ad21276e9e0fadd319eb9390835ba.tab")

descriptives_comments("data/Pietitie niet anoniem page_592411374140027_2014_01_15_15_07_19461acb511ca1b3ca8b6669d423cfdf_comments.tab")
descriptives_comments("data/Zwarte piet is racisme niet anoniem page_296568710371104_2014_01_15_16_03_6b6ad21276e9e0fadd319eb9390835ba_comments.tab")

descriptives_users("data/Zwarte piet is racisme niet anoniem page_296568710371104_2014_01_15_16_03_6b6ad21276e9e0fadd319eb9390835ba.gdf")

descriptives_users("data/Pietitie niet anoniem page_592411374140027_2014_01_15_15_07_19461acb511ca1b3ca8b6669d423cfdf.gdf")
