#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv 
import sys
import re
import feedparser
import os.path
import urllib.request, urllib.error, urllib.parse
import time
import csv
import os
import datetime
import urllib

#import http.cookiejar

from urllib import request
from time import sleep
from random import randint
from lxml import html

from nieuwsparsers import *



#stuff for ad on-the-fly download
class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)        
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = urllib.request.HTTPCookieProcessor()

opener = urllib.request.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib.request.install_opener(opener)



def parse (medium, doc, ids, titel):
    '''
    This is a function that calls the right parser
    It returns nothing, but saves the parsed contents to a series of 
    csv-files
    '''

    if medium=="nu" or medium=="nunieuw":
        print("I just chose the nu parser")
        elements=parse_nu(doc,ids,titel)
    #elif medium=="ad":
        #print("I just chose ad parser.")
        #elements=parse_ad(doc,ids,titel)
    elif medium=="volkskrant":
        print("I just chose the VK-parser")
        elements=parse_vk(doc,ids,titel)
    elif medium=="nrc":
        print("I just chose nrc parser")
        elements=parse_nrc(doc,ids,titel)
    elif medium=="telegraaf":
        print("I just chose Tele parser")
        elements=parse_telegraaf(doc,ids,titel)
    elif medium=="spits":
        print("I just chose Spits parser")
        elements=parse_spits(doc,ids,titel)
    elif medium=="metronieuws":
        print("I just chose Metro parser")
        elements=parse_metronieuws(doc,ids,titel)
    elif medium=="trouw":
        print("I just chose Trouw parser")
        elements=parse_trouw(doc,ids,titel)
    elif medium=="parool":
        print("I just chose Parool parser")
        elements=parse_parool(doc,ids,titel)
    elif medium=="nos":
        print("I just chose NOS parser")
        elements=parse_nos(doc,ids,titel)
    elif medium=="tpo":
        print("I just chose Tpo parser")
        elements=parse_tpo(doc,ids,titel)
    elif medium=="geenstijl":
        print("I just chose Geenstijl parser")
        elements=parse_geenstijl(doc,ids,titel)
    elif medium=="sargasso":
        print("I just chose Sargasso parser")
        elements=parse_sargasso(doc,ids,titel)
    elif medium=="fok":
        print("I just chose Fok parser")
        elements=parse_fok(doc,ids,titel)
    else:
        print("Er bestaat nog geen parser voor "+medium)
        return

    #print("Type of elements is: ",type(elements))
    listelements=list(elements)
    #print("Type of listelements is: ",type(listelements))
    #print(listelements)
    csvname="artikelen/"+medium+"/parsed/{0:06d}".format(len(ids))+".csv"   
    with open(csvname, mode="w",encoding="utf-8") as fit:
          writer=csv.writer(fit)
          for element in listelements:
              writer.writerow([element,])



#Function that checks feeds defined here
def checkfeeds(waarvandaan, waarnaartoe):
    waarnaartoestem=waarnaartoe.split(".")[0]
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
            os.makedirs("artikelen/"+waarnaartoestem)
            os.makedirs("artikelen/"+waarnaartoestem+"/parsed")
        except: 
            print("Er ging iets mis met het aanmaken van de map artikelen/"+waarnaartoestem+" en de map artikelen/"+waarnaartoestem+"/parsed"+"\nJe zal even zelf moeten uitzoeken waar het probleem ligt.")
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
            filename="artikelen/"+waarnaartoestem+"/"+waarnaartoestem+"{0:06d}".format(len(artikel_id))+".html" 
            #try:
            if 1==1:
                if waarnaartoestem=="volkskrant":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.volkskrant.nl//cookiewall/accept?url="+mylink
                    #req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})          
                    req=urllib.request.Request((mylink))          
                elif waarnaartoestem=="ad":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.ad.nl/ad/acceptCookieCheck.do?url="+mylink
                    #req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})
                    req=urllib.request.Request((mylink))
                elif waarnaartoestem=="trouw":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.trouw.nl/tr/acceptCookieCheck.do?url="+mylink
                    #req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})
                    req=urllib.request.Request((mylink))
                elif waarnaartoestem=="parool":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.parool.nl/parool/acceptCookieCheck.do?url="+mylink
                    #req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})
                    req=urllib.request.Request((mylink))
                    print(mylink)
                else: 
                    req=urllib.request.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
                response = urllib.request.urlopen(req)
                #httpcode=response.getcode()
                #cj=http.cookiejar.CookieJar()
                #opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
                #response=opener.open(re.sub("/$","",post.link))
                artikelopslaan=open(filename,mode="w",encoding="utf-8")
                artikelopslaan.write(response.read().decode(encoding="utf-8",errors="ignore"))
                artikelopslaan.close()
                with open(filename,"r",encoding="utf-8",errors="ignore") as f: 
                  fx=f.read()
                  parse(waarnaartoestem,fx,artikel_id,re.sub(r"\n|\r\|\t"," ",post.title))

            #except:
            #    print("Het downloaden van "+re.sub("/$","",post.link)+" is niet gelukt.")
            #    print("Bestandsnaam: "+filename)
            #    filename="DOWNLOAD-ERROR"
            artikel_filename.append(filename)
            i=i=1
    output=list(zip(artikel_id,artikel_datum,artikel_kop,artikel_teaser,artikel_link,artikel_filename))
    with open(waarnaartoe,mode="w",encoding="utf-8") as csvfile:
        writer=csv.writer(csvfile,delimiter=",")
        writer.writerows(output)
    if nieuweposts==0:
        print("0 nieuwe artikelen gevonden op "+waarvandaan)
    else:
        print(str(nieuweposts)+"/"+str(len(d.entries)),"nieuwe artikelen gevonden op "+waarvandaan+". "+waarnaartoe+" is bijgewerkt en de artikelen zijn gedownload")



# begin program

if __name__ == "__main__":
    print("\n")
    print("Welkom bij rsshond 0.2 (by Damian Trilling, www.damiantrilling.net)")
    print("Current date & time: " + time.strftime("%c"))
    print("\n")

    with open("sources.conf",mode="r",encoding="utf-8") as csvfile:
        reader=csv.reader(csvfile,delimiter=",")
        for row in reader:
            #try:
                checkfeeds (row[1],row[0])
            #except:
            #    print("\nERROR CHECKING "+row[1])
            #    print("CHECK THE FILE "+row[0]+" FOR CONSISTENCY\n")
