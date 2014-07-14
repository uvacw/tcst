#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
import urllib
import csv, codecs, cStringIO
import sys
import re
import feedparser
import os.path
import urllib2
import time

class CsvUnicodeWriter(object):
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        # If we want BOM add line: self.stream.write(codecs.BOM_UTF8)
    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
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




def checkfeeds(waarvandaan, waarnaartoe):
	d = feedparser.parse(waarvandaan)
	artikel_id=[]
	artikel_datum=[]
	artikel_kop=[]
	artikel_teaser=[]
	artikel_link=[]
	artikel_filename=[]
	if os.path.isfile(waarnaartoe):
		reader=CsvUnicodeReader(open(waarnaartoe,"rb"))
		i=0
		for row in reader:
			i=i+1
			#print "\r",str(i)," ",
			#sys.stdout.flush()
			artikel_id.append(row[0])
			artikel_datum.append(row[1])
                        artikel_kop.append(row[2])
			artikel_teaser.append(row[3])
			artikel_link.append(row[4])
			artikel_filename.append(row[5])
		# print str(i),"items gevonden in "+waarnaartoe
	else:
		print waarnaartoe,"bestaat nog niet, wordt nu aangemaakt. Ook een map voor de artikelen wordt aangemaakt."
                try:
                    os.makedirs("artikelen/"+waarnaartoe.split(".")[0])
                except:
                    print "Er ging iets mis met het aanmaken van de map artikelen/"+waarnaartoe.split(".")[0]+"\nJe zal even zelf moeten uitzoeken waar het probleem ligt."
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
                                req = urllib2.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
				response = urllib2.urlopen(req)
				httpcode=response.getcode()
				artikelopslaan=open(filename,"wb")
				artikelopslaan.write(response.read())
				artikelopslaan.close()
			except:
				print "Het downloaden van "+re.sub("/$","",post.link)+" is niet gelukt."
				print "Bestandsnaam: "+filename
				filename="DOWNLOAD-ERROR"
			artikel_filename.append(filename)	
			i=i=1
	if nieuweposts==0:
		print "0 nieuwe artikelen gevonden op "+waarvandaan
	else:
		print str(nieuweposts)+"/"+str(len(d.entries)),"nieuwe artikelen gevonden op "+waarvandaan+". "+waarnaartoe+" is bijgewerkt en de artikelen zijn gedownload"
		output=zip(artikel_id,artikel_datum,artikel_kop,artikel_teaser,artikel_link,artikel_filename)
		writer=CsvUnicodeWriter(open(waarnaartoe,"wb"))
		writer.writerows(output)


# begin program

print "\n"
print "Welkom bij rsshond 0.1 (by Damian Trilling, www.damiantrilling.net)"
print "Current date & time: " + time.strftime("%c")
print "\n"

reader=CsvUnicodeReader(open("sources.conf","rb"))
i=0
for row in reader:
	i=i+1
	# print "Feed nummer "+str(i)+": Adres "+row[1]+" , bestandsnaam "+row[0]
	try:
            checkfeeds (row[1],row[0])
        except:
            print "\nERROR CHECKING "+row[1]
            print "CHECK THE FILE "+row[0]+" FOR CONSISTENCY\n"




