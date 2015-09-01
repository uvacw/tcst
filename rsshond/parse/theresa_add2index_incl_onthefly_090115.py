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

#%%
'''
def clean_doc(doc):
    result = ''
    for line in doc:
        if line != '\n':
	    if line.strip() and not any([
                line[0] in ['{', '}'],
                line.startswith('if'),
                line.startswith('NU.Lazy'),
                line.startswith('Foto'),
                line.startswith('Door:'),
                line.startswith('var id')
            ]):
                result += (line + ' ')
    return result.strip()
'''
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

'''
def tokenize(doc):
    tokens = [e.lower() for e in wordpunct_tokenize(doc) if e not in ['.','?','!']]
    for tok in tokens:
        if tok[-1] in [".","'",'"']: tok = tok[:-1]
        if len(tok)>2 and tok[0] in ["'",'"']: tok = tok[1:]
    return tokens
'''
  
def parse(doc, medium, ids):
    if medium=="nu" or medium=="nunieuw":
       return parse_nu(doc, ids)
    elif medium=="ad":
        return parse_ad(doc, ids)
    elif medium=="volkskrant":
        return parse_vk(doc, ids)
    elif medium=="nrc":
        return parse_nrc(doc,ids)
    elif medium=="telegraaf":
        return parse_telegraaf(doc, ids)
    elif medium=="spits":
        return parse_spits(doc, ids)
    elif medium=="metronieuws":
        return parse_metronieuws(doc, ids)


def parse_nu(doc, ids):
    tree = html.fromstring(doc)
    try:
        #category = tree.xpath('//*[@class="block-wrapper section-nu"]/div/ul/li[2]/a/text()')[0]
        category = tree.xpath('//*[@class="block breadcrumb "]/div/div/ul/li[2]/a/text()')[0]
        if category == "":
            print("OOps - geen category for", ids,"?")
    except:
        category=""
        print("OOps - geen category for", ids,"?")
    try:
        #textfirstpara=tree.xpath('//*[@id="block-288801"]/div/div[1]/div[2]/text()')[0]
        textfirstpara=tree.xpath('//*[@data-type="article.header"]/div/div[1]/div[2]/text()')[0]
    except:
        print("OOps - geen eerste alinea for", ids,"?")
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
        textrest=tree.xpath('//*[@data-type="article.body"]/div/div/p/text() \
        | //*[@data-type="article.body"]/div/div/p/span/text() \
        | //*[@data-type="article.body"]/div/div/p/em/text() \
        | //*[@data-type="article.body"]/div/div/h2/text() \
        | //*[@data-type="article.body"]/div/div/p/a/em/text() \
        | //*[@data-type="article.body"]/div/div/p/em/a/text() \
        | //*[@data-type="article.body"]/div/div/p/a/text() \
        | //*[@data-type="article.body"]/div/div/p/strong/text()')   
        if textrest ==[]:
            print("OOps - empty textrest for", ids,"?")
    except:
        print("OOps - geen text for", ids,"?")
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
                print("OOps - geen author for", ids, "?")
    except:
        author_door="" 
        print("OOps - geen author for", ids, "?")
    text=polish(text)
    author_bron = ""
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()


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
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        print(doc)
        return("","","", "")
    try:
        category=tree.xpath('//*[@class="action-bar__primary"]/div/a/text()')[0]
    except:
        category=""
    if category=="":
        try:
            category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0]
        except:
            category=""
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip() #\//*[@class="intro"]/text()
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
        #
        #5. path: old design regular text
        #6. path: old design second heading
        #7. path:old design text with link
        textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() \
        | //*[@class="article__body__container"]/p/text() \
        | //*[@class="article__body__container"]/h3/text() \
        | //*[@class="article__body__container"]/p/a/text() \
        \
        | //*[@id="art_box2"]/p/text() \
        | //*[@id="art_box2"]/p/strong/text() \
        | //*[@id="art_box2"]/p/a/text()')
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
    if author_door=="":
        try:
            author_door= tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
            if author_door=="edactie":
                author_door = "redactie"            
        except:
            author_door=""
    try:    
        author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip() # geeft het tweede veld: "Bron: ANP"
    except:
        author_bron=""
    if author_bron=="":
        try:
            author_bron=" ".join(tree.xpath('//*/span[@class="author-info__source"]/text()')).strip().lstrip("- ").lstrip("Bron: ").strip() 
        except:
            author_bron=""
    if author_bron=="":
        try:
            bron_text = tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", bron_text)[0]
        except:
            author_bron=""
        if author_bron=="":
            try:
                bron_text = tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
                author_bron = re.findall(".*?bron:(.*)", bron_text)[0]
            except:
                author_bron==""                
    if author_door=="" and author_bron=="" and category=="Opinie":
        author_door = "OPINION PIECE OTHER AUTHOR"
    text=polish(text)
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()


def parse_nrc(doc, ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        print(doc)
        return("","","", "")
    try:
        category = tree.xpath('//*[@id="broodtekst"]/a[1]/text()')[0]
    except:
        category = ""
        #print("OOps - geen category for", ids, "?")
    try:
        #1. path: type 1 layout: regular text
        #2. path: type 1 layout: text with link behind
        #3. path: type 1 layout: text bold
        #4. path: type 1 layout: text bold and italic
        #5. path: type 2 layout: normal text first paragraph
        #6. path: type 2 layout: text with link behind
        #7. path: type 1 layout: italic text, found in 2014 11 988
        textfirstpara=tree.xpath('//*[@class="eerste"]/text() \
        | //*[@class="eerste"]/a/text() \
        | //*[@class="eerste"]/strong/text() \
        | //*[@class="eerste"]/strong/em/text() \
        | //*[@id="article-content"]/p[1]/text() \
        | //*[@id="article-content"]/p[1]/a/text() \
        | //*[@class="eerste"]/em/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
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
        textrest=tree.xpath('//*[@id="broodtekst"]/p[position()>1]/text() \
        | //*[@id="broodtekst"]/h2/text() \
        | //*[@id="article-content"]/p[position()>1]/text() \
        | //*[@id="article-content"]/p[position()>1]/strong/text() \
        | //*[@id="article-content"]/p[position()>1]/a/text() \
        | //*[@id="article-content"]/p[position()>1]/em/text() \
        | //*[@id="article-content"]/h2/text() \
        | //*[@id="article-content"]/blockquote/p/text() \
        | //*[@id="broodtekst"]/p[position()>1]/a/text() \
        | //*[@id="broodtekst"]/blockquote/p/text() \
        | //*[@id="broodtekst"]/p[position()>1]/strong/text() \
        | //*[@id="broodtekst"]/p[position()>1]/a/em/text() \
        | //*[@class="beschrijving"]/text() \
        | //*[@class="beschrijving"]/a/text() \
        | //*[@class="beschrijving"]/a/em/text() \
        | //*[@id="broodtekst"]/p[position()>1]/em/text()')
    except:
        #print("oops - geen text?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door = tree.xpath('//*[@class="author"]/span/a/text()')[0]
    except:
        author_door = ""
    if author_door == "":
        try:
            author_door = tree.xpath('//*[@class="auteur"]/span/a/text()')[0]
        except:
            author_door = ""
    author_bron=""
    text=polish(text)
    if text=="" and category=="" and author_door=="":
        print("No article-page for", ids, "?")
        try:
            if tree.xpath('//*[@class="kies show clearfix"]/h2/text()')[0] == 'Lees dit hele artikel':
                text="THIS SEEMS TO BE AN ARTICLE ONLY FOR SUBSCRIBERS"
                print(ids, ": This seems to be a subscribers-only article")   
        except:
            text=""
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()
    

def parse_telegraaf(doc, ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        #print(doc)
        return("","","","")
    try:
        category = tree.xpath('//*[@class="selekt"]/text()')[0]
    except:
        category = ""
        print("OOps - geen category for", ids, "?")
    try:
        #1.path: layout 1: regular first para
        #2.path: layout 2 (video): regular first (and mostly only) para
        #3.path: layout 1: second version of first para, fi 2014 11 6
        textfirstpara=tree.xpath('//*[@class="zak_normal"]/p/text() \
        | //*[@class="bodyText streamone"]/div/p/text() \
        | //*[@class="zak_normal"]/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
        print("OOps - geen textfirstpara for", ids, "?")
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
        print("oops - geen texttest for", ids, "?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door = tree.xpath('//*[@class="auteur"]/text()')[0].strip().lstrip("Van ").lstrip("onze").lstrip("door ").strip()
    except:
        author_door = ""
    author_bron=""
    text=polish(text)
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()

def parse_spits(doc, ids):
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
        #
        #21. path: another version of italic text fi 2014 06 626
        #22. path: another version of italic text with link behind, fi 2014 06 1024
        #23. path: yet another regular text, fi 2014 06 1471
        #24. path: again, regular text, fi 2014 06 1547
        #25. path: text with link, matches text in path 24, fi 2014 06 1547
        #
        #26. path: bold text, matches text in path 24, fi 2014 06 1547
        #27. path: another regula rtext, fi 2014 05 437
        #28. path: italic text, fits path 27., fi 2014 05 437
        #30. path: again regular text, fi 2014 04 50
        #31. path: text with link behind, fi 2014 04 50
        #
        #32. path: another regular text, fi 2014 03 667
        #33. path: 2nd heading, matches 32. patch, fi 2014 03 667
        #33. path: text with link, matches 32. patch, fi 2014 03 667
        textrest=tree.xpath('//*[@class="field-item even"]/p/text() \
        | //*[@class="field-item even"]/p/a/text() \
        | //*[@class="field-item even"]/p/em/text() \
        | //*[@class="field-item even"]/h2/text() \
        | //*[@class="field-item even"]/p/span/text() \
        | //*[@class="field-item even"]/h2/span/text() \
        | //*[@class="field-item even"]/p/span/em/a/text() \
        | //*[@class="field-item even"]/p/em/a/text() \
        \
        | //*[@class="article"]/p/text() \
        | //*[@class="article"]/p/a/text() \
        | //*[@class="article"]/p/em/text() \
        | //*[@class="article"]/p/strong/text() \
        | //*[@class="article"]/div/text() \
        | //*[@class="article"]/div/strong/text() \
        | //*[@class="article"]/div/em/text() \
        \
        | //*[@class="article"]/div/div/p/text() \
        | //*[@class="article"]/div/p/text() \
        | //*[@class="article"]/p/em/a/text() \
        | //*[@class="article"]/p/span/text() \
        | //*[@class="article"]/p/span/a/text() \
        \
        | //*[@class="article"]/p/span/em/text() \
        | //*[@class="article"]/p/a/em/text()\
        | //*[@class="article"]/div/div/div/p/text() \
        | //*[@class="article"]/div/div/text() \
        | //*[@class="article"]/div/div/a/text() \
        \
        | //*[@class="article"]/div/div/strong/text() \
        | //*[@id="artikelKolom"]/div/div/p/text() \
        | //*[@id="artikelKolom"]/div/div/p/em/text() \
        | //*[@class="article"]/p/font/text() \
        | //*[@class="article"]/p/font/a/text() \
        \
        | //*[@class="article"]/div/div/div/text() \
        | //*[@class="article"]/div/div/div/strong/text() \
        | //*[@class="article"]/div/div/div/a/text()')
    except:
        print("oops - geen texttest for", ids, "?")
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
year = "2014" #possib: 2013, 2014, 2015
months = ["aug"] #possib: "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "okt", "nov", "dec" 
onthefly = True

for month in months:
    
    print("--------------Start month:", month)
    
    if year=="2013" and month=="dec":
        directory = "/home/theresa/hiwi_sachen/201312/rsshond-bak"
    elif year=="2014" and month=="jan":
        directory = "/home/theresa/hiwi_sachen/201401/rsshond"
    elif year=="2014" and month=="feb":
        directory = "/home/theresa/hiwi_sachen/201402/rsshond"
    elif year=="2014" and month=="mar":
        directory = "/home/theresa/hiwi_sachen/201403/rsshond"
    elif year=="2014" and month=="apr":
        directory = "/home/theresa/hiwi_sachen/201404/rsshond-april"
    elif year=="2014" and month=="may":
        directory = "/home/theresa/hiwi_sachen/201405/rsshond"
    elif year=="2014" and month=="jun":
        directory = "/home/theresa/hiwi_sachen/201406/rsshond-juni"
    elif year=="2014" and month=="jul":
        directory = "/home/theresa/hiwi_sachen/201407/rsshond-juli-3"
    elif year=="2014" and month=="aug":
        directory = "/home/theresa/hiwi_sachen/201408/var/www/rsshond-augustus"
    elif year=="2014" and month=="sep":
        directory = "/home/theresa/hiwi_sachen/201409/rsshond-september"
    elif year=="2014" and month=="okt":
        directory = "/home/theresa/hiwi_sachen/201410/rsshond-september"
    elif year=="2014" and month=="nov":
        directory = "/home/theresa/hiwi_sachen/201411/var/www/rsshond-november"
    elif year=="2014" and month=="dec":
        directory = "/home/theresa/hiwi_sachen/201412/rsshond-december"
    elif year=="2015" and month=="jan":
        directory = "/home/theresa/hiwi_sachen/201501/rsshond-januari"
    elif year=="2015" and month=="feb":
        directory = "/home/theresa/hiwi_sachen/201502-03/rsshond-febmaart" 
    else:
        print("Could not find the right directory, no data for year or month available?")
        break
        
    os.chdir(directory)
    
    
    if __name__ == '__main__':
        
        
        # specify which media to add to the index:
        media=["metronieuws"]
        for medium in media:
            
            if onthefly==False:
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
                                rawhtml=open(row[5],encoding="utf-8",mode="r").read() 
                            except:
                                print("Tried to download the following url:",row[5], "id:", ids)
                                print("That did not work, skipping this one")
                                continue
        
                            #parse the html:                    
                            text,category,author_door, author_bron =parse(rawhtml,medium, ids)
                            
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
    
                
            elif onthefly== True and medium=="nu" or onthefly==True and medium=="nunieuw" or onthefly==True and medium=="volkskrant" or onthefly==True and medium=="metronieuws":
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
            
            elif onthefly==True and medium=="ad":
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
    
#%% 
###################
### TRAIL CODE ####
###################

#trial from machine                
test = open("/home/theresa/hiwi_sachen/201401/rsshond/artikelen/volkskrant/volkskrant000046.html",encoding="utf-8",mode="r").read()
test_html = html.fromstring(test)
parse_vk(test, 1)
#test_html.xpath('//*[@id="broodtekst"]/p/text()')
#%% trial on-the-fly
url_long = "http://s.vk.nl/3760149"
req = request.Request(url_long, headers={'User-Agent' : "Mozilla/5.0"})
data = request.urlopen(req).read()
test = data.decode(encoding="utf-8",errors="ignore").replace("\n"," ").replace("\t"," ")
test_html = html.fromstring(test)
#%%
def parse_vk_trial(doc, ids):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc), ids)
        print(doc)
        return("","","", "")
    try:
        category=tree.xpath('//*[@class="action-bar__primary"]/div/a/text()')[0]
    except:
        category=""
    if category=="":
        try:
            category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0]
        except:
            category=""
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip() #\//*[@class="intro"]/text()
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
        #
        #5. path: old design regular text
        #6. path: old design second heading
        #7. path:old design text with link
        textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() \
        | //*[@class="article__body__container"]/p/text() \
        | //*[@class="article__body__container"]/h3/text() \
        | //*[@class="article__body__container"]/p/a/text() \
        \
        | //*[@id="art_box2"]/p/text() \
        | //*[@id="art_box2"]/p/strong/text() \
        | //*[@id="art_box2"]/p/a/text()')
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
    if author_door=="":
        try:
            author_door= tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
            if author_door=="edactie":
                author_door = "redactie"            
        except:
            author_door=""
    try:    
        author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip() # geeft het tweede veld: "Bron: ANP"
    except:
        author_bron=""
    if author_bron=="":
        try:
            author_bron=" ".join(tree.xpath('//*/span[@class="author-info__source"]/text()')).strip().lstrip("- ").lstrip("Bron: ").strip() 
        except:
            author_bron=""
    if author_bron=="":
        try:
            bron_text = tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
            author_bron = re.findall(".*?bron:(.*)", bron_text)[0]
        except:
            author_bron=""
        if author_bron=="":
            try:
                bron_text = tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
                author_bron = re.findall(".*?bron:(.*)", bron_text)[0]
            except:
                author_bron==""                
    if author_door=="" and author_bron=="" and category=="Opinie":
        author_door = "OPINION PIECE OTHER AUTHOR"
    text=polish(text)
    return text.strip(),category.strip(),author_door.replace("\n"," ").strip(),author_bron.replace("\n"," ").strip()

    
parse_vk_trial(test, 1)