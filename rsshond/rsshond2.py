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
#from elasticsearch import Elasticsearch                                                                                                                                            from lxml import html
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
from lxml import html

#stuff for ad on-the-fly download
class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        #print ("Cookie Manip Right Here")
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)        
    http_error_301 = http_error_303 = http_error_307 = http_error_302

cookieprocessor = urllib.request.HTTPCookieProcessor()

opener = urllib.request.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib.request.install_opener(opener)


#not working yet
#def polish(textstring):
    #lines = textstring.strip().split('\n')
    #lead = lines[0].strip()
    #rest = ' '.join( [l.strip() for l in lines[1:] if l.strip()] )

    #if rest: result = lead + ' || ' + rest
    #else: result = lead

    #remove double \n 's etc
    #lines = textstring.replace("\r","\n").split("\n")
    #result = "\n".join([line for line in lines if line])
   
    #Paragraohs are anow seperated by a single \n. We'll replace it by "    ", to avoid problems with the output in both the elastic search web interface and the CSV export
    # still think about wether that's the best way to somehow keep the info where a paragraph brake is...
    #result=result.replace("\n","    ")
    #return result.strip()

#Parser voor Volkskrant
def parse_vk(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        #print(doc)
        return("","","", "")
    try:
        category=tree.xpath('//*[@class="action-bar__primary"]/div/a/text()')[0]
    except:
        category=""
    if category=="":
        try:
            category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0] 
            #print("Category: ")
            #print(category)
        except:
            category="" 
            print("oops - geen category")
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()  
        #print("First para: ")
        #print(textfirstpara)
        #print("Type")
        #print(type(textfirstpara))
    except:
        textfirstpara=""
    if textfirstpara=="":
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[1].replace("\n", "").strip()
        except:
            textfirstpara=" "
            print("oops - geen first para")
    try:
        #1. path: regular textrest 
        #2. path: textrest version found in 2014 11 16
        #3. path: second heading found in 2014 11 50
        #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
        #5. path: old design regular text
        #6. path: old design second heading
        #7. path:old design text with link        
        textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() | //*[@class="article__body__container"]/p[*]/text() | //*[@class="article__body__container"]/h3/text() | //*[@class="article__body__container"]/p/a/text() | //*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/strong/tex() | //*[@id="art_box2"]/p/a/text() | //*/p[@class="article__body__paragraph first"]/text()')
        #print("Text rest: ")
        #print(textrest)
    except:
        print("oops - geen text?")
        textrest=""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    #print("Text: ")
    #print(text)
    try:
        author_door=" ".join(tree.xpath('//*/span[@class="author"]/*/text() | //*/span[@class="article__body__container"]/p/sub/strong/text()')).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
        #print("Author: ")
        #print(author_door)
        # geeft het eerste veld: "Bewerkt \ door: Redactie"  
        if author_door=="edactie":
            author_door = "redactie"
    except:
        author_door=""
    if author_door=="":
        try:
            author_door=tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
            if author_door=="edactie":
                author_door = "redactie"
        except:
            author_door=""
            print("oops - geen auhtor?")
    try:
        author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip()
        # geeft het tweede veld: "Bron: ANP"                          
    except:
        author_bron=""
    if author_bron=="":
        try:
            author_bron=" ".join(tree.xpath('//*/span[@class="author-info__source"]/text()')).strip().lstrip("- ").lstrip("Bron: ").strip()
        except:
            author_bron=""
    if author_bron=="":
        try:
            bron_text=tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
            author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
        except:
            author_bron=""
        if author_bron=="":
            try:
                bron_text=tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
                author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
            except:
                author_bron=""
                print("oops - geen bron")
    if author_door=="" and author_bron=="" and category=="Opinie":
        author_door = "OPINION PIECE OTHER AUTHOR"
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/volkskrant/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(text)
        artcategory.append(category)
        artauthor_door.append(author_door)
        artauthor_bron.append(author_bron)
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")

#Parser voor Nu 
def parse_nu(doc,ids):
    tree = html.fromstring(doc)
    try:
        #category = tree.xpath('//*[@class="block-wrapper section-nu"]/div/ul/li[2]/a/text()')[0]
        category = tree.xpath('//*[@class="block breadcrumb "]/div/div/ul/li[2]/a/text()')[0]
        if category == "":
            print("OOps - geen category?")
    except:
        category=""
        print("OOps - geen category?")
    try:
        #textfirstpara=tree.xpath('//*[@id="block-288801"]/div/div[1]/div[2]/text()')[0]
        textfirstpara=tree.xpath('//*[@data-type="article.header"]/div/div[1]/div[2]/text()')[0]
    except:
        print("OOps - geen eerste alinea?")
        textfirstpara=""
    try:
        #1.path: regular paragraphs 
        #2.path: paragraphs with xpath"span" included 
        #3.path: italic text found in: nunieuw jan 2015 96
        #4.path: second order heading found in: nunieuw jan 2015 227
        #5.path: link+italic (displayed underlined) text found in: nunieuw jan 2015 1053
        #6.path: second version for link+italic (displayed underlined) text found in: nunieuw jan 2015 4100
        #7.path: link (displayed underlined, not italic) text found in: nunieuw dec 2014 5
        #8.path: bold text found in: nunieuw nov 2014 12
        textrest=tree.xpath('//*[@data-type="article.body"]/div/div/p/text() | //*[@data-type="article.body"]/div/div/p/span/text()| //*[@data-type="article.body"]/div/div/p/em/text() | //*[@data-type="article.body"]/div/div/h2/text() | //*[@data-type="article.body"]/div/div/h3/text() | //*[@data-type="article.body"]/div/div/p/a/em/text() | //*[@data-type="article.body"]/div/div/p/em/a/text() | //*[@data-type="article.body"]/div/div/p/a/text() | //*[@data-type="article.body"]/div/div/p/strong/text()')   
        if textrest == "":
            print("OOps - empty textrest for?")
    except:
        print("OOps - geen text?")
        textrest=""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        #regular author-xpath:
        author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Door:").strip()
        if author_door == "":
            # xpath if link to another hp is embedded in author-info            
            try: 
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                print("OOps - geen author for?")
    except:
        author_door="" 
        print("OOps - geen author?")
    #text=polish(text)
    author_bron = ""
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/nu/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(text.strip())
        artcategory.append(category.strip())
        artauthor_door.append(author_door.strip())
        artauthor_bron.append(author_bron.strip())
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")


#Parser for Nrc
def parse_nrc(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        print(doc)
        return("","","", "")
    try:
        category = tree.xpath('//*[@id="broodtekst"]/a[1]/text()')[0]
    except:
        category = ""
    if category=="":
        try:
            category=tree.xpath('//*[@class="article__section-branding"]/text()')[0]
        except:
            category=""
        #print("OOps - geen category for", ids, "?")
    try:
        #1. path: type 1 layout: regular text
        #2. path: type 1 layout: text with link behind
        #3. path: type 1 layout: text bold
        #4. path: type 1 layout: text bold and italic
        #5. path: type 2 layout: normal text first paragraph
        #6. path: type 2 layout: text with link behind
        #7. path: type 1 layout: italic text, found in 2014 11 988
        #8. path for in beeld found 2015 11 13
        textfirstpara=tree.xpath('//*[@class="eerste"]/text() | //*[@class="eerste"]/a/text() | //*[@class="eerste"]/strong/text() | //*[@class="eerste"]/strong/em/text() | //*[@id="article-content"]/p[1]/text() | //*[@id="article-content"]/p[1]/a/text() | //*[@class="eerste"]/em/text() | //*[@class="intro"]/text() | //*[@class="intro"]/p/text() | //*[@class="intro"]/p/span/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
        print("Ooops geen first para")
    try:
        #1. path: type 1 layout: regular text
        #2. path: type 1 layout: second heading in regular text
        #3. path: type 2 layout: text in different layout, found in 2014 12 11
        #4. path: type 2 layout: bold text, found in 2014 12 11
        #5. path: type 2 layout: text with underlying link, found in 2014 12 11
        #6. path: type 2 layout: italic text, found in 2014 12 11
        #7. path: type 2 layout: second heading found in 2014 12 11
        #8. path: type 2 layout: text in grey box/ speech bubble
        #9. path: type 1 layout: text with link behind
        #10.path: type 1 layout: text in grey box/ speech bubble
        #11. path: type 1 layout: bold text found in 2014 12 198
        #12. path: type 1 layout: italix text with link behind, found in 2014 12 198 !!!!!not working :(
        #13. path: type 3 layout: regular text found in 2014 11 62
        #14. path: type 3 layout: text with link behind found in 2014 11 63
        #15. path: type 3 layout: italic text with link behind, found in 2014 11 63
        #16. path: type 1 layout: italix text, found in 2014 04 500
        #17. path: type 1 layout: found 2015 11 13
        #17. path: type 1 layout: heading in regular text found 2015 11 13
        #18. live feed subheading "old news"
        #19. live feed text "old news"
        #20. live feed textlink "oldnews"
        #21. live feed list "old news"
        #21. live feed subheading "new news"
        #22. live feed text "new news"
        #23. live feed textlink "new news"
        #24. live feed names "new news"
        #24. path type 1 layout: subheading in regular text found 2015 11 16
        #25. path type 1 layout: text in link found on 2015 11 16
        #26. path regular layout: bold subtitle found 2015 11 16
        textrest=tree.xpath('//*[@id="broodtekst"]/p[position()>1]/text() | //*[@id="broodtekst"]/h2/text() | //*[@id="article-content"]/p[position()>1]/text() | //*[@id="article-content"]/p[position()>1]/strong/text() | //*[@id="article-content"]/p[position()>1]/a/text() | //*[@id="article-content"]/p[position()>1]/em/text() | //*[@id="article-content"]/h2/text() | //*[@id="article-content"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/a/text() | //*[@id="broodtekst"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/strong/text() | //*[@id="broodtekst"]/p[position()>1]/a/em/text() | //*[@class="beschrijving"]/text() | //*[@class="beschrijving"]/a/text() | //*[@class="beschrijving"]/a/em/text() | //*[@id="broodtekst"]/p[position()>1]/em/text() | //*[@class="content article__content"]/p[position()>0]/text() | //*[@class="content article__content"]/p/strong/text() | //*[@class="content article__content"]/p/a/text() | //*[@class="content article__content"]/blockquote/p/text() | //*[@class="bericht"]/h2/text() | //*[@class="bericht"]/p/text() | //*[@class="bericht"]/p/a/text() |//*[@class="bericht"]/ul/li/text() | //*[@class="bericht bericht--new"]/h2/text() | //*[@class="bericht bericht--new"]/p/text() | //*[@class="bericht bericht--new"]/p/a/text() | //*[@class="bericht bericht--new"]/p/em/text() | //*[@class="content article__content"]/h2/text() | //*[@class="content article__content"]/h3/text() | //*[@class="content article__content"]/p/a/em/text() | //*[@class="content article__content"]/blockquote/p/strong/text() | //*[@class="content article__content"]/p/br/a/strong/text()')
    except:
        print("oops - geen text?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    textnew=re.sub("Follow @nrc_opinie","",text)
    try:
        author_door = tree.xpath('//*[@class="author"]/span/a/text()')[0]
    except:
        author_door = ""
    if author_door == "":
        try:
            author_door = tree.xpath('//*[@class="auteur"]/span/a/text()')[0]
        except:
            author_door = ""
    if author_door == "":
        try:
            author_door = tree.xpath('//*[@class="authors"]/ul/li/text()')[0]
        except:
            author_door = ""
    if author_door=="":
        try: 
            author_door=tree.xpath('//*[@class="article__byline__author-and-date"]/a/text()')[0]
        except:
            author_door = ""
    author_bron=""
    #text=polish(text)
    if textnew=="" and category=="" and author_door=="":
        print("No article-page?")
        try:
            if tree.xpath('//*[@class="kies show clearfix"]/h2/text()')[0] == 'Lees dit hele artikel':
                text="THIS SEEMS TO BE AN ARTICLE ONLY FOR SUBSCRIBERS"
                print(" This seems to be a subscribers-only article")   
        except:
            text=""
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_door=[]
        csvname="artikelen/nrc/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(textnew)
        artcategory.append(category)
        artauthor_door.append(author_door)
        elements=zip(arttext,artcategory,artauthor_door)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")
    
def parse_ad(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        #print(doc)
        #return("","","", "")
    try:
        category = tree.xpath('//*[@id="actua_arrow"]/a/span/text()')[0]
    except:
        category=""
        print("OOps - geen category?")
    #1. path: regular intro
    #2. path: intro when in <b>; found in a2014 04 130
    textfirstpara=tree.xpath('//*[@id="detail_content"]/p/text() | //*[@class="intro"]/b/text()')
    #1. path: regular text
    #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057
    #3. path: second hadings found in 2014 11 1425
    textrest = tree.xpath('//*[@id="detail_content"]/section/p/text() | //*[@id="detail_content"]/section/p/a/text() | //*[@id="detail_content"]/section/p/strong/text()')
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
            print("OOps - geen author?")
    try:
        brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
        author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
    except:
        author_bron=""    
    #text=polish(text)
    if text=="" and category=="" and author_door=="":
        print("No article-page?")
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/ad/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(text)
        artcategory.append(category)
        artauthor_door.append(author_door)
        artauthor_bron.append(author_bron)
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")

def parse_telegraaf(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        #print(doc)
        return("","","","")
    try:
        category = tree.xpath('//*[@class="selekt"]/text()')[0]
    except:
        category = ""
        print("OOps - geen category?")
    try:
        #1.path: layout 1: regular first para
        #2.path: layout 2 (video): regular first (and mostly only) para
        #3.path: layout 1: second version of first para, fi 2014 11 6
        #4.path layout 1: place found on 2015 11 16
        textfirstpara=tree.xpath('//*[@class="zak_normal"]/p/text() \
        | //*[@class="bodyText streamone"]/div/p/text() \
        | //*[@class="zak_normal"]/text() | //*[@class="zak_normal"]/span/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
        print("OOps - geen textfirstpara?")
    try:
        #1. path: layout 1: regular text, fi 2014 12 006
        #2. path: layout 1: text with link, fi 2014 12 006
        #3. path: layout 1: second heading, fi 2014 12 015
        #4. path: layout 1: bold text, fi 2014 12 25
        #5. path: layout 1: italic text, fi 2014 09 5200
        #6. path: layout 1: second headings, fi 2014 07 84
        textrest=tree.xpath('//*[@id="artikelKolom"]/p/text() \
        | //*[@id="artikelKolom"]/p/a/text() \
        | //*[@id="artikelKolom"]/h2/strong/text() \
        | //*[@id="artikelKolom"]/p/strong/text() \
        | //*[@id="artikelKolom"]/p/em/text() \
        | //*[@id="artikelKolom"]/h2/text()')
    except:
        print("oops - geen texttest?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door = tree.xpath('//*[@class="auteur"]/text()')[0].strip().lstrip("Van ").lstrip("onze").lstrip("door").strip()
    except:
        author_door = ""
    author_bron=""
    #text=polish(text)
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/telegraaf/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(text)
        artcategory.append(category)
        artauthor_door.append(author_door)
        artauthor_bron.append(author_bron)
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")

def parse_spits(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        #print(doc)   
        return("","","","")
    try:
        category = tree.xpath('//*[@class="active"]/text()')[0]
    except:
        category = ""
        print("OOps - geen category?")
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
        #old layout:
        #9. path: regular text
        #10. path: text with link behind, fi 2014 08 12
        #11. path: italic text, fi 2014 08 19
        #12. path: second heading, fi 2014 08 411
        #13. path: another version of regular text, fi 2014 08 840
        #14. path: second heading fitting 13.path regular text, fi 2014 08 840
        #15. path: italic text, fitting 13. path, fi 2014 08 840
        #seems like again another layout/html-structure
        #16. path: regular text, fi 2014 07 749
        #17. path: also regular text, fi 2014 07 749
        #18. path: (probabaly second layout): underlined, text with link, fi 2014 07 1251
        #19. path: and another version of regular text fi 2014 06 626
        #20. path: text with link behind, fi 2014 06 626
        #21. path: another version of italic text fi 2014 06 626
        #22. path: another version of italic text with link behind, fi 2014 06 1024
        #23. path: yet another regular text, fi 2014 06 1471
        #24. path: again, regular text, fi 2014 06 1547
        #25. path: text with link, matches text in path 24, fi 2014 06 1547
        #26. path: bold text, matches text in path 24, fi 2014 06 1547
        #27. path: another regula rtext, fi 2014 05 437
        #28. path: italic text, fits path 27., fi 2014 05 437
        #30. path: again regular text, fi 2014 04 50
        #31. path: text with link behind, fi 2014 04 50
        #32. path: another regular text, fi 2014 03 667
        #33. path: 2nd heading, matches 32. patch, fi 2014 03 667
        #33. path: text with link, matches 32. patch, fi 2014 03 667
        textrest=tree.xpath('//*[@class="field-item even"]/p/text() | //*[@class="field-item even"]/p/a/text() | //*[@class="field-item even"]/p/em/text() | //*[@class="field-item even"]/h2/text() | //*[@class="field-item even"]/p/span/text() | //*[@class="field-item even"]/h2/span/text() | //*[@class="article"]/div/p/text() | //*[@class="field-item even"]/p/span/em/a/text() | //*[@class="field-item even"]/p/em/a/text() | //*[@class="article"]/p/a/text() | //*[@class="article"]/p/em/text() | //*[@class="article"]/p/strong/text() | //*[@class="article"]/div/text() | //*[@class="article"]/div/strong/text() | //*[@class="article"]/div/em/text() | //*[@class="article"]/div/div/p/text() | //*[@class="article"]/div/p/text() | //*[@class="article"]/p/em/a/text() | //*[@class="article"]/p/span/text() | //*[@class="article"]/p/span/a/text() | //*[@class="article"]/p/span/em/text() | //*[@class="article"]/p/a/em/text() | //*[@class="article"]/div/div/div/p/text() | //*[@class="article"]/div/div/text() | //*[@class="article"]/div/div/a/text() | //*[@class="article"]/div/div/strong/text() |//*[@id="artikelKolom"]/div/div/p/text() | //*[@id="artikelKolom"]/div/div/p/em/text() | //*[@class="article"]/p/font/text() | //*[@class="article"]/p/font/a/text() | //*[@class="article"]/div/div/div/text() | //*[@class="article"]/div/div/div/strong/text() | //*[@class="article"]/div/div/div/a/text()')
    except:
        print("oops - geen texttest?")
        textrest = ""
    #text = textfirstpara + "\n"+ "\n".join(textrest)
    text = "\n".join(textrest)
    try:
        #new layout author:
        author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").strip()
    except:
        author_door = ""
    if author_door=="": 
        #try old layout author
        try:
            author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
        except:
            author_door = ""        
    author_bron=""
    #text=polish(text)
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/spits/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(text)
        artcategory.append(category)
        artauthor_door.append(author_door)
        artauthor_bron.append(author_bron)
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")

def parse_metronieuws(doc,ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
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
        #10. path: bold and italic text, fi 2014 12 04
        #11. path: bold text, fi 2014 12 04
        #12. path: second headings
        #13. path: regular text
        textrest=tree.xpath('//*[@class="field-item even"]/p/text() | //*[@class="field-item even"]/p/a/text() | //*[@class="field-item even"]/p/em/text() | //*[@class="field-item even"]/h2/text() | //*[@class="field-item even"]/p/span/text() | //*[@class="field-item even"]/h2/span/text() | //*[@class="field-item even"]/p/span/em/a/text() | //*[@class="field-item even"]/p/em/a/text() | //*[@class="field-item even"]/p/em/strong/text() | //*[@class="field-item even"]/p/b/text() | //*[@class="field-item even"]/div/text() | //*[@class="field-item even"]/p/strong/text()') 
    except:
        print("oops - geen textrest?")
        textrest = ""
        #text = textfirstpara + "\n"+ "\n".join(textrest)
        #textnew=re.sub("Lees ook:"," ",textrest)
    text = "\n".join(textrest)
    textnew=re.sub("Lees ook:"," ",text)
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
    #text=polish(text)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    #text=polish(text)
#    arttext=[]
 #   artcategory=[]
  #  artauthor_bron=[]
   # artauthor_door=[]
    #csvname="artikelen/volkskrant/parsed/"+artikel_id+".csv"
    try:
        arttext=[]
        artcategory=[]
        artauthor_bron=[]
        artauthor_door=[]
        csvname="artikelen/metronieuws/parsed/"+str(len(ids))+".csv"
        print(csvname)
        arttext.append(textnew)
        artcategory.append(category)
        artauthor_door.append(author_door)
        artauthor_bron.append(author_bron)
        elements=zip(arttext,artcategory,artauthor_door,artauthor_bron)
        with open(csvname, mode="w",encoding="utf-8") as fit:
            writer=csv.writer(fit)
            writer.writerows(elements)
    except:
        print("File not saved")

 

 # function that calls the right parser
def parse (medium, doc, ids):
    #try:
    if medium=="nu" or medium=="nunieuw":
        print("I just chose the nu parser")
        parse_nu(doc,ids)
    elif medium=="ad":
        print("I just chose ad parser.")
        parse_ad(doc,ids)
    elif medium=="volkskrant":
        print("I just chose the VK-parser")
        parse_vk(doc,ids)
    elif medium=="nrc":
        print("I just chose nrc parser")
        parse_nrc(doc,ids)
    elif medium=="telegraaf":
        print("I just chose Tele parser")
        parse_telegraaf(doc,ids)
    elif medium=="spits":
        print("I just chose Spits parser")
        parse_spits(doc,ids)
    elif medium=="metronieuws":
        print("I just chose Metro parser")
        parse_metronieuws(doc,ids)
    else:
        print("Er bestaat nog geen parser voor"+medium)

#except:
    #    print("Parser kan niet kiesen.")

#Function that checks feeds defined here
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
            waarnaartoestem=waarnaartoe.split(".")[0]
            os.makedirs("artikelen/"+waarnaartoestem)
            os.makedirs("artikelen/"+waarnaartoestem+"/parsed")
        except: 
            print("Er ging iets mis met het aanmaken van de map /artikelen/"+waarnaartoe.split(".")[0]+" en de map /artikelen/"+waarnaartoe.split(".")[0]+"/parsed"+"\\Je zal even zelf moeten uitzoeken waar het probleem ligt.")
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
            try:
                if waarnaartoestem=="volkskrant":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.volkskrant.nl//cookiewall/accept?url="+mylink
                    req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})          
                elif waarnaartoestem=="ad":
                    mylink=re.sub("/$","",post.link)
                    mylink="http://www.ad.nl/ad/acceptCookieCheck.do?url="+mylink
                    req=urllib.request.Request((mylink), headers={'User-Agent' : "Wget/1.9"})
                else: 
                    req=urllib.request.Request(re.sub("/$","",post.link), headers={'User-Agent' : "Wget/1.9"})
                response = urllib.request.urlopen(req)
                #httpcode=response.getcode()
                artikelopslaan=open(filename,mode="w",encoding="utf-8")
                artikelopslaan.write(response.read().decode(encoding="utf-8",errors="ignore"))
                artikelopslaan.close()
            except:
                print("Het downloaden van "+re.sub("/$","",post.link)+" is niet gelukt.")
                print("Bestandsnaam: "+filename)
                filename="DOWNLOAD-ERROR"
            artikel_filename.append(filename)
            with open(filename,"r",encoding="utf-8",errors="ignore") as f: 
                fx=f.read()
                parse(waarnaartoestem,fx,artikel_id)
            #except:
                #print("Something goes wrong with opening the file")
                #parse(waarnaartoestem, f)
            #except:
                #print("AAaaAAAaaa")
                #print(f)
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
