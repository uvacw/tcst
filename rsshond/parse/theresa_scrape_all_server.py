#!/usr/bin/env python3
from __future__ import unicode_literals
import csv
#from elasticsearch import Elasticsearch
from lxml import html
#es = Elasticsearch()
#from nltk.tokenize import wordpunct_tokenize
#import re
import os
import datetime
import urllib
from urllib import request
from time import sleep
from random import randint
import re

#%% what should be scraped and parsed?
year = "2014" #possib: 2013, 2014, 2015
months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"] #possib: "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" 
media=["metronieuws"]
os.chdir("/home/theresa")

#%%
#stuff for ad on-the-fly download
class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        print ("Cookie Manip Right Here")
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)        
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = urllib.request.HTTPCookieProcessor()

opener = urllib.request.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib.request.install_opener(opener)


def polish(textstring):
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = ' '.join( [l.strip() for l in lines[1:] if l.strip()] )

    if rest: result = lead + ' || ' + rest
    else: result = lead

    # remove double \n 's etc
    #lines = textstring.replace("\r","\n").split("\n")
    #result = "\n".join([line for line in lines if line])
   
    # Paragraohs are anow seperated by a single \n. We'll replace it by "    ", to avoid problems with the output in both the elastic search web interface and the CSV export
    # still think about wether that's the best way to somehow keep the info where a paragraph brake is...
    #result=result.replace("\n","    ")

    return result.strip()

  
def parse(doc, medium, ids):
    if medium=="ad":
        return parse_ad(doc, ids)
    elif medium=="volkskrant":
        return parse_vk(doc, ids)
    elif medium=="metronieuws":
        return parse_metronieuws(doc, ids)


def parse_ad(doc, ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        print(doc)
        return("","","", "")
    try:
        category = tree.xpath('//*[@id="actua_arrow"]/a/span/text()')[0]
    except:
        category=""
        print("OOps - geen category for", ids, "?")
    #1. path: regular intro
    #2. path: intro when in <b>; found in a2014 04 130
    textfirstpara=tree.xpath('//*[@id="detail_content"]/p/text() | \
    //*[@class="intro"]/b/text()')
    #1. path: regular text
    #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057
    #3. path: second hadings found in 2014 11 1425
    textrest = tree.xpath('//*[@id="detail_content"]/section/p/text() \
    | //*[@id="detail_content"]/section/p/a/text() \
    | //*[@id="detail_content"]/section/p/strong/text()')
    text = "\n".join(textfirstpara) + "\n" + "\n".join(textrest)
    try:
        author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
    except:
        author_door=""
    if author_door=="":
        try:
            author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()                       
        except:
            author_door==""
            print("OOps - geen author for", ids, "?")
    try:
        brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
        author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
    except:
        author_bron=""    
    text=polish(text)
    if text=="" and category=="" and author_door=="":
        print("No article-page for", ids, "?")
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.strip()


def parse_vk(doc, ids):
    tree = html.fromstring(doc)
    try:
        category=tree.xpath('//*/header/div/div[4]/div[1]/div/a/text()')[0]
    except:
        category=""
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()
    except:
        #print("OOps - geen eerste alinea for", ids, "?") #,any articles have no first line; commented out because it slows down the code.
        textfirstpara=""
    if textfirstpara=="":
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[1].replace("\n", "").strip()
        except:
            textfirstpara=""            
    try:
        #1. path: regular textrest
        #2. path: textrest version found in 2014 11 16 
        #3. path: second heading found in 2014 11 50
        #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
        textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() \
        | //*[@class="article__body__container"]/p/text() \
        | //*[@class="article__body__container"]/h3/text() \
        | //*[@class="article__body__container"]/p/a/text()')
    except:
        print("oops - geen text?")
        textrest=""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door=" ".join(tree.xpath('//*/span[@class="author"]/*/text() \
        | //*/span[@class="article__body__container"]/p/sub/strong/text()')).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()   # geeft het eerste veld: "Bewerkt door: Redactie"
        if author_door=="edactie":
            author_door = "redactie"
    except:
        author_door=""
    try:    
        author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip() # geeft het tweede veld: "Bron: ANP"
    except:
        author_bron=""
    if author_door=="" and author_bron=="" and category=="Opinie":
        author_door = "OPINION PIECE OTHER AUTHOR"
    text=polish(text)
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()


def parse_metronieuws(doc, ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        #print(doc)   
        return("","","","")
    try:
        category = tree.xpath('//*[@class="active"]/text()')[0]
    except:
        category = ""
        #print("OOps - geen category for", ids, "?")
    #fix: xpath for category in new layout leads to a sentence in old layout:
    if len(category.split(" ")) >1:
        category=""            
    try:
        #1. path: regular text
        #2. path: text with link behind, fi 2014 12 646
        #3. path: italic text, fi 2014 12 259
        #4. path: second headings, fi 2014 12 222
        #5. path: another version of regualr formated text, fi 2014 12 1558
        #6. path: another version a second heading, fi 2014 12 1923
        #7. path: italic text with link behind in span environment, fi 2014 11 540
        #8. path: italic text with link behind, not in span evir, fi 2014 10 430
        
        #--until here code is just copied from spits
        #
        #10. path: bold and italic text, fi 2014 12 04
        #11. path: bold text, fi 2014 12 04
        #12. path: second headings
        #13. path: regular text
        textrest=tree.xpath('//*[@class="field-item even"]/p/text() \
        | //*[@class="field-item even"]/p/a/text() \
        | //*[@class="field-item even"]/p/em/text() \
        | //*[@class="field-item even"]/h2/text() \
        | //*[@class="field-item even"]/p/span/text() \
        | //*[@class="field-item even"]/h2/span/text() \
        | //*[@class="field-item even"]/p/span/em/a/text() \
        | //*[@class="field-item even"]/p/em/a/text() \
        \
        | //*[@class="field-item even"]/p/em/strong/text() \
        | //*[@class="field-item even"]/p/strong/text() \
        | //*[@class="field-item even"]/p/b/text() \
        | //*[@class="field-item even"]/div/text()')
    except:
        print("oops - geen texttest for", ids, "?")
        textrest = ""
    #text = textfirstpara + "\n"+ "\n".join(textrest)
    text = "\n".join(textrest)
    try:
        #new layout author:
        author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").lstrip("© ").lstrip("2014 ").strip()
    except:
        author_door = ""
    if author_door=="": 
        #try old layout author
        try:
                author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
        except:
            author_door = ""        
    author_bron=""
    text=polish(text)
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()  
    

def change_date(date, medium):
    if medium=="nu" or medium=="nunieuw" or medium=="spits" or medium=="metronieuws":
       return change_date_nu_spits_metronieuws(date)
    elif medium=="ad" or medium=="volkskrant" or medium=="telegraaf":
        return change_date_ad_vk_telegraaf(date)
    

def change_date_nu_spits_metronieuws(date):
    oldpattern = "%a, %d %b %Y %H:%M:%S %z"
    newpattern = "%d-%m-%Y"
    old_date = datetime.datetime.strptime(date, oldpattern)
    new_date = old_date.strftime(newpattern)
    return(new_date)


def change_date_ad_vk_telegraaf(date):
    date_ohnegtm = date.replace(" GMT", "")
    oldpattern = "%a, %d %b %Y %H:%M:%S"
    newpattern = "%d-%m-%Y"
    old_date = datetime.datetime.strptime(date_ohnegtm, oldpattern)
    new_date = old_date.strftime(newpattern) + " GMT"
    return(new_date)

#%%
for month in months:
    
    print("--------------Start month:", month)
    
    if year=="2014" and month=="jan":
        directory = "/home/theresa/jan"
    elif year=="2014" and month=="feb":
        directory = "/home/theresa/feb"
    elif year=="2014" and month=="mar":
        directory = "/home/theresa/mar"
    elif year=="2014" and month=="apr":
        directory = "/home/theresa/apr"
    elif year=="2014" and month=="may":
        directory = "/home/theresa/may"
    elif year=="2014" and month=="jun":
        directory = "/home/theresa/jun"
    elif year=="2014" and month=="jul":
        directory = "/home/theresa/jul"
    elif year=="2014" and month=="aug":
        directory = "/home/theresa/aug"
    elif year=="2014" and month=="sep":
        directory = "/home/theresa/sep"
    elif year=="2014" and month=="oct":
        directory = "/home/theresa/oct"
    elif year=="2014" and month=="nov":
        directory = "/home/theresa/nov"
    elif year=="2014" and month=="dec":
        directory = "/home/theresa/dec"
    else:
        print("Could not find the right directory, no data for year or month available?")
        break
        
    os.chdir(directory)

    
    if __name__ == '__main__':
        
        for medium in media:
                        
            if medium=="volkskrant" or medium=="metronieuws":
                indexname = 'nlnieuws'
    
                ids = 1
                numberoferrors=0
                print("\n\nStarting to import",medium,"\n")
                with open("artikelen_p/"+medium+"_"+year+month+"_docname.csv", mode = "w") as table_docname:
                    writer_docname=csv.writer(table_docname)
                    writer_docname.writerow(["url_short", "url_long", "date_long", "date_short", "title", "teaser", "filename_raw", "door", "bron", "category", "filename_parsed"])
                    with open("artikelen_p/"+medium+"_"+year+month+"_fulltext.csv", mode = "w") as table_fulltext:
                        writer_fulltext=csv.writer(table_fulltext)
                        writer_fulltext.writerow(["url_short", "url_long", "date_long", "date_short", "title", "teaser", "door", "bron", "category", "filename_parsed", "fulltext"])
                        
                        reader=csv.reader(open(medium+".csv"))
                        for row in reader:
                            url= row[0]
                            outlet = medium
                            date_long = row[1]
                            title = row[2]
                            teaser = row[3]
                            url_long = row[4]
                            filename_raw = row[5]
                            try:
                                req = request.Request(url_long, headers={'User-Agent' : "Mozilla/5.0"})
                                data = request.urlopen(req).read()
                                rawhtml = data.decode(encoding="utf-8",errors="ignore").replace("\n"," ").replace("\t"," ")
                                print("Downloaded number",ids)
                            except:
                                print("Tried to download the following url:", url_long, "id:", ids)
                                print("That did not work. To be sure, we'll try one more time after having waited for some seconds. In addition, we'll add a no-cache header")
                                try:
                                    sleep(10)
                                    req = request.Request(url_long, headers={'User-Agent' : "Mozilla/5.0", 'Pragma': 'no-cache'})
                                    data = request.urlopen(req).read()
                                    rawhtml = data.decode(encoding="utf-8",errors="ignore").replace("\n"," ").replace("\t"," ")
                                    print ("Great, now it works! No need to worry.")
                                except:
                                    print("OK, no chance. Giving up this one.")
                                    numberoferrors+=1
                                    continue
                            
                            #parse the html:                    
                            text,category,author_door, author_bron=parse(rawhtml,medium, ids)
                            
                            #create short date:
                            date_short = change_date(date_long, medium)
                            
                            #save text-file:
                            nr=str(100000+ids)
                            with open("artikelen_p/"+medium+"/"+medium+year+month+nr+".txt", "w") as text_file:
                                text_file.write(text)
                            filename_parsed = "artikelen_p/"+medium+"/"+medium+year+month+nr+".txt"
                            #write the tables
                            writer_docname.writerow([url, url_long, date_long, date_short, title, teaser, filename_raw, author_door, author_bron, category, filename_parsed])
                            writer_fulltext.writerow([url, url_long, date_long, date_short, title, teaser, author_door, author_bron, category, filename_parsed, text])
                          
                            #print(text,category,author)
                            #tokens = tokenize(title + ' ' + text)
                            #es.index(index=indexname, doc_type='article', id=ids, body={'source': outlet, 'date': date, 'author': author, 'category':category, 'title': title, 'teaser': teaser, 'url': url, 'url_long': url_long,'text': text, 'localhtml': row[5]})
                            ids += 1
                            sleep(randint(1,5))
                print(numberoferrors,"errors while processing",medium)
            
            elif medium=="ad":
                indexname = 'nlnieuws'
    
                ids = 1
                numberoferrors=0
                print("\n\nStarting to import",medium,"\n")
                with open("artikelen_p/"+medium+"_"+year+month+"_docname.csv", mode = "w") as table_docname:
                    writer_docname=csv.writer(table_docname)
                    writer_docname.writerow(["url_short", "url_long", "date_long", "date_short", "title", "teaser", "filename_raw", "door", "bron", "category", "filename_parsed"])
                    with open("artikelen_p/"+medium+"_"+year+month+"_fulltext.csv", mode = "w") as table_fulltext:
                        writer_fulltext=csv.writer(table_fulltext)
                        writer_fulltext.writerow(["url_short", "url_long", "date_long", "date_short", "title", "teaser", "door", "bron", "category", "filename_parsed", "fulltext"])
                      
                        reader=csv.reader(open(medium+".csv"))
                        for row in reader:
                            url= row[0]
                            outlet = medium
                            date_long = row[1]
                            title = row[2]
                            teaser = row[3]
                            url_long = row[4]
                            filename_raw = row[5]
                            try:
                                url_long2="http://www.ad.nl/ad/acceptCookieCheck.do?url="+url_long
                                data = urllib.request.urlopen(url_long2).read()
                                rawhtml = data.decode(encoding="utf-8",errors="ignore").replace("\n"," ").replace("\t"," ")
                                print("Downloaded number",ids)
                            except:
                                print("Tried to download the following url:", url_long, "id:", ids)
                                print("It did not work, going on")
                                continue
                            #parse the html:                    
                            text,category,author_door, author_bron=parse(rawhtml,medium, ids)
                            
                            #create short date:
                            date_short = change_date(date_long, medium)
                            
                            #save text-file:
                            nr=str(100000+ids)
                            with open("artikelen_p/"+medium+"/"+medium+year+month+nr+".txt", "w") as text_file:
                                text_file.write(text)
                            filename_parsed = "artikelen_p/"+medium+"/"+medium+year+month+nr+".txt"
                            #write the tables
                            writer_docname.writerow([url, url_long, date_long, date_short, title, teaser, filename_raw, author_door, author_bron, category, filename_parsed])
                            writer_fulltext.writerow([url, url_long, date_long, date_short, title, teaser, author_door, author_bron, category, filename_parsed, text])
                          
                            #print(text,category,author)
                            #tokens = tokenize(title + ' ' + text)
                            #es.index(index=indexname, doc_type='article', id=ids, body={'source': outlet, 'date': date, 'author': author, 'category':category, 'title': title, 'teaser': teaser, 'url': url, 'url_long': url_long,'text': text, 'localhtml': row[5]})
                            ids += 1
                            sleep(randint(1,5))
                            print(numberoferrors,"errors while processing",medium)
        
            else:
                print("You chose a onthefly-medium combination for which we don't have code.")


print("Done :) ")
    