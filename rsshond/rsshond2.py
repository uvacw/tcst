#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv 
import sys
import re
import feedparser
import os.path
import urllib.request, urllib.error, urllib.parse
import time

def checkfeeds(waarvandaan, waarnaartoe):
    d = feedparser.parse(waarvandaan)
    artikel_id=[]
    artikel_datum=[]
    artikel_kop=[]
    artikel_teaser=[]
    artikel_link=[]
    artikel_filename=[]
    if os.path.isfile(waarnaartoe):
        with open(waarnaartoe,mode="r",encoding="utf-8") as csvfile:
            reader=csv.reader(csvfile,delimiter=",")
            i=0
            for row in reader:
                artikel_id.append(row[0])
                artikel_datum.append(row[1])
                artikel_kop.append(row[2])
                artikel_teaser.append(row[3])
                artikel_link.append(row[4])
                artikel_filename.append(row[5])
    else:
        print(waarnaartoe,"bestaat nog niet, wordt nu aangemaakt. Ook een map voor de artikelen wordt aangemaakt.")
        try:
            os.makedirs("artikelen/"+waarnaartoe.split(".")[0])
        except:
            print("Er ging iets mis met het aanmaken van de map artikelen/"+waarnaartoe.split(".")[0]+"\nJe zal even zelf moeten uitzoeken waar het probleem ligt.")
    nieuweposts=0
    for post in d.entries:
        i=0
        # sommige feeds (bijvoorbeeld die van joop.nl) laten het identificatieveld leeg, in dat geval gebruiken we de link in plaats van het id-veld
        try:
            identificatie=post.id
        except:
            identificatie=post.link
        if identificatie not in artikel_id:
            nieuweposts+=1
            artikel_id.append(identificatie)
            artikel_datum.append(post.published)
            artikel_kop.append(re.sub(r"\n|\r\|\t"," ",post.title))
            try:
                artikel_teaser.append(re.sub(r"\n|\r\|\t"," ",post.description))
            except:
                artikel_teaser.append("teaser empty")
            artikel_link.append(re.sub("/$","",post.link))
            waarnaartoestem=waarnaartoe.split(".")[0]
            filename="artikelen/"+waarnaartoestem+"/"+waarnaartoestem+"{0:06d}".format(len(artikel_id))+".html" 
            try:
                # req = urllib2.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Mozilla/5.0"})
                req = urllib.request.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
                response = urllib.request.urlopen(req)
                httpcode=response.getcode()
                artikelopslaan=open(filename,"wb")
                artikelopslaan.write(response.read())
                artikelopslaan.close()
            except:
                print("Het downloaden van "+re.sub("/$","",post.link)+" is niet gelukt.")
                print("Bestandsnaam: "+filename)
                filename="DOWNLOAD-ERROR"
            artikel_filename.append(filename)       
            i=i=1
    if nieuweposts==0:
        print("0 nieuwe artikelen gevonden op "+waarvandaan)
    else:
        print(str(nieuweposts)+"/"+str(len(d.entries)),"nieuwe artikelen gevonden op "+waarvandaan+". "+waarnaartoe+" is bijgewerkt en de artikelen zijn gedownload")
        output=list(zip(artikel_id,artikel_datum,artikel_kop,artikel_teaser,artikel_link,artikel_filename))
        with open(waarnaartoe,mode="w",encoding="utf-8") as csvfile:
            writer=csv.writer(csvfile,delimiter=",")
            writer.writerows(output)


# begin program

if __name__ == "__main__":
    print("\n")
    print("Welkom bij rsshond 0.2 (by Damian Trilling, www.damiantrilling.net)")
    print("Current date & time: " + time.strftime("%c"))
    print("\n")

    with open("sources.conf",mode="r",encoding="utf-8") as csvfile:
        reader=csv.reader(csvfile,delimiter=",")
        for row in reader:
            try:
                checkfeeds (row[1],row[0])
            except:
                print("\nERROR CHECKING "+row[1])
                print("CHECK THE FILE "+row[0]+" FOR CONSISTENCY\n")
