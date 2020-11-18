#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twitter import *
import json
import time
import csv

consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


#screennames=["polcomm","uvacw","ALLTHENENAMESYOUWANTTOFOLLOW"]

screennames=[]
with open('../input/accounts.csv', encoding='utf-8') as fi:
	reader=csv.reader(fi)
	for row in reader:
		screennames.append(row[1].strip().lstrip('@'))



auth = OAuth(access_key, access_secret, consumer_key, consumer_secret)
twitter = Twitter(auth = auth)




start_time=time.time()
apicallsin15min=0

def getposts(tweep, maxid):
	global start_time
	global apicallsin15min
	if time.time()-start_time<870 and apicallsin15min >178:
		print ("We issued "+str(apicallsin15min)+" API requests in the last "+str(int(time.time()-start_time))+" seconds. Twitter allows 180 calls per 900 seconds. We will wait for "+str(int(900-(time.time()-start_time)))+" seconds.")
		time.sleep(900-(time.time()-start_time))
		print ("Let's continue!")
		# reset timer and apicall-counter
		apicallsin15min=0
		start_time=time.time()	
	
	apicallsin15min+=1
	if not maxid:
		try:
			posts=twitter.statuses.user_timeline(screen_name=tweep, count=200)
		except:
			posts={}
			return posts
	else:
		try:
			posts=twitter.statuses.user_timeline(screen_name=tweep, count=200, max_id=maxid)
		except:
			posts={}
			return posts
	return posts


allposts={}

i=0
for tweep in screennames:
	i+=1
	print ("Starting to collect tweets by",tweep,"("+str(i)+"/"+str(len(screennames))+")")
	print ("API-calls in the last 15 minutes:"+str(apicallsin15min))
	posts=getposts(tweep,None)
	nieuweposts=posts
	while len(posts) < 3001:
		try:
			maxid=nieuweposts[-1]["id"]
		except:
			break
		nieuweposts=getposts(tweep,maxid)
		if len(nieuweposts)<=1:
			break
		print ("\tDownloaded a batch of"+str(len(nieuweposts))+"tweets - continuing...")
		posts+=nieuweposts
	allposts[tweep]=posts
	print ("Downloaded"+str(len(posts))+"tweets by"+tweep)

# volledige dump	
#with open("output/allposts.json",encoding="utf-8",mode="w") as fo:
#	fo.write(json.dumps(allposts, ensure_ascii=False,indent=1))

with open("../output/allposts.json",mode="w") as fo:	
	json.dump(allposts,fo)

# per username

for tweep in screennames:
	print ("writing data for "+tweep)
	with open("../output/"+tweep+".tab", encoding="utf-8", mode = "w") as fo:
		headers=["text","retweeted","retweet_count","hashtags","urls","created_at","description","screen_name","name","friends_count","followers_count","statuses_count"]
		fo.write("\t".join(headers)+"\n")
		for post in allposts[tweep]:
			output=[]
			output.append(post["text"].replace("\t"," ").replace("\n"," ").replace("\r"," "))
			output.append(str(post["retweeted"]))
			output.append(str(post["retweet_count"]))			
			hashtags = [tag["text"] for tag in post["entities"]["hashtags"]]		
			output.append(str(hashtags))
			urls = [u["expanded_url"] for u in post["entities"]["urls"]]	
			output.append(str(urls))	
			output.append(post["created_at"])
			output.append(post["user"]["description"].replace("\t"," ").replace("\n"," ").replace("\r"," "))
			output.append(tweep)
			output.append(post["user"]["name"].replace("\t"," ").replace("\n"," ").replace("\r"," "))
			output.append(str(post["user"]["friends_count"]))
			output.append(str(post["user"]["followers_count"]))
			output.append(str(post["user"]["statuses_count"]))			
			fo.write("\t".join(output)+"\n")
