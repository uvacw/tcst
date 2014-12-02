#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from io import open
from pattern.nl import sentiment
from os import walk
from os.path import isfile, join, splitext
import argparse

def analyze_lexisnexis(pathwithlnfiles,outputfilename):
    """
    Usage: insert_lexisnexis(pathwithlnfiles,recursive)
    pathwithlnfiles = path to a directory where lexis nexis output is stored
    recursive: TRUE = search recursively all subdirectories, but include only files ending on .txt
               FALSE = take ALL files from directory supplied, but do not include subdirectories
    """
    tekst = {}
    byline = {}
    section = {}
    length = {}
    loaddate = {}
    language = {}
    pubtype = {}
    journal = {}
    sentiment_pol = {}
    sentiment_sub= {}
    lnsourcefile = {}
    alleinputbestanden = []
    for path, subFolders, files in walk(pathwithlnfiles):
        for f in files:
            if isfile(join(path, f)) and splitext(f)[1].lower() == ".txt":
                alleinputbestanden.append(join(path, f))
    artikel = 0
    with open(outputfilename,"w",encoding="utf-8") as fo:
        for bestand in alleinputbestanden:
            print "Now processing", bestand
            with open(bestand, "r", encoding="utf-8") as f:
                i = 0
                for line in f:
                    i = i + 1
                    # print "Regel",i,": ", line
                    line = line.replace("\r", " ")
                    if line == "\n":
                        continue
                    matchObj = re.match(r"\s+(\d+) of (\d+) DOCUMENTS", line)
                    if matchObj:
                        # eerst even


                        artikel += 1
                        tekst[artikel] = ""
                        continue
                    if line.startswith("BYLINE"):
                        byline[artikel] = line.replace("BYLINE: ", "").rstrip("\n")
                    elif line.startswith("SECTION"):
                        section[artikel] = line.replace("SECTION: ", "").rstrip("\n")
                    elif line.startswith("LENGTH"):
                        length[artikel] = line.replace("LENGTH: ", "").rstrip("\n").rstrip(" woorden")
                    elif line.startswith("LOAD-DATE"):
                        loaddate[artikel] = line.replace("LOAD-DATE: ", "").rstrip("\n")
                    elif line.startswith("LANGUAGE"):
                        language[artikel] = line.replace("LANGUAGE: ", "").rstrip("\n")
                    elif line.startswith("PUBLICATION-TYPE"):
                        pubtype[artikel] = line.replace("PUBLICATION-TYPE: ", "").rstrip("\n")
                    elif line.startswith("JOURNAL-CODE"):
                        journal[artikel] = line.replace("JOURNAL-CODE: ", "").rstrip("\n")
                    elif line.lstrip().startswith("Copyright ") or line.lstrip().startswith("All Rights Reserved"):
                        pass
                    elif line.lstrip().startswith("AD/Algemeen Dagblad") or line.lstrip().startswith(
                            "De Telegraaf") or line.lstrip().startswith("Trouw") or line.lstrip().startswith(
                            "de Volkskrant") or line.lstrip().startswith("NRC Handelsblad") or line.lstrip().startswith(
                            "Metro") or line.lstrip().startswith("Spits"):
                        pass
                    else:
                        tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
        print "Done!", artikel, "articles read."

        if not len(journal) == len(loaddate) == len(section) == len(language) == len(byline) == len(length) == len(tekst):
            print "!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "Ooooops! Not all articles seem to have data for each field. These are the numbers of fields that where correctly coded (and, of course, they should be equal to the number of articles, which they aren't in all cases."
            print "journal", len(journal)
            print "loaddate", len(loaddate)
            print "section", len(section)
            print "language", len(language)
            print "byline", len(byline)
            print "length", len(length)
            print "tekst", len(tekst)
            print "!!!!!!!!!!!!!!!!!!!!!!!!!"
            print
            print "Anyhow, we're gonna proceed and set those invalid fields to 'NA'. However, you should be aware of this when analyzing your data!"


        else:
            print "No missing values encountered."

        for i in range(artikel):
            try:
                art_source = journal[i + 1]
            except:
                art_source = "NA"
            try:
                art_date = loaddate[i + 1]
            except:
                art_date = "NA"
            try:
                art_section = section[i + 1]
            except:
                art_section = "NA"
            try:
                art_language = language[i + 1]
            except:
                art_language = "NA"
            try:
                art_length = length[i + 1]
            except:
                art_length = "NA"
            try:
                art_text = tekst[i + 1]
            except:
                art_text = "NA"
            try:
                art_byline = byline[i + 1]
            except:
                art_byline = "NA"
            try:
                art_sentiment_sub = str(sentiment_sub[i +1])
            except:
                art_sentiment_sub = "NA"
            try:
                art_sentiment_pol = str(sentiment_sub[i +1])
            except:
                art_sentiment_pol = "NA"

            try:
                art_lnsource=lnsourcefile[i+1]
            except:
                art_lnsource="NA"
            fo.write(art_lnsource+"\t"+art_source.lower()+"\t"+art_date+"\t"+art_section.lower()+"\t"+art_language.lower()+"\t"+art_length+"\t"+art_byline+"\t"+art_text.replace("\t"," ").replace("\n"," ").replace("\r"," ")+"\t"+art_sentiment_sub+"\t"+art_sentiment_pol+"\n")


if __name__ == '__main__':

    print "lnsentiment 0.1 Copyright (C) 2014  Damian Trilling"
    print "This program comes with ABSOLUTELY NO WARRANTY."
    print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
    print "\n"
    parser = argparse.ArgumentParser(
    description="This program sentiment-analyzes lexis-nexis articles")
    parser.add_argument("outputfile", help = "How should the output table be named?")
    parser.add_argument("folder", help = "The folder in which lexis nexis files are stored")


    args = parser.parse_args()

    analyze_lexisnexis(args.folder,args.outputfile)