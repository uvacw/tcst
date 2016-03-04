#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to determine overlap based on
cosine distance and levenshtein distance
STILL NEEDS SOME MODFIFICATION AND DOCUMENTATION TO BE REUSABLSE
'''


import datetime
import csv
from collections import defaultdict
import sys
import unicodedata
import scipy as sp
import numpy as np


from sklearn.feature_extraction.text import TfidfVectorizer





aantalartikelen=defaultdict(int)
comparisons=defaultdict(list)
overlap=defaultdict(list)
overlap2=defaultdict(int)
overlap3=defaultdict(list)


STOPWORDS=open('damianstop.txt').readlines()
STARTDATE=datetime.date(2014,1,1)
THRESHOLD=0.6


tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))

def remove_punctuation(text):
    return text.replace("`","").replace("´","").translate(tbl)


def datetoint(datum):
    datumsplit=[int(i) for i in datum.split("-")]
    return (datetime.date(datumsplit[2],datumsplit[1],datumsplit[0])-STARTDATE).days





def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)
    if len(target) == 0:
        return len(source)
    source = np.array(tuple(source))
    target = np.array(tuple(target))
    previous_row = np.arange(target.size + 1)
    for s in source:
        current_row = previous_row + 1
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)
        previous_row = current_row
    return previous_row[-1]









i=0
foutjes=0
with open('damiantest.csv') as metafile:
    reader=csv.reader(metafile,delimiter=';')
    for row in reader:
        try:
            with open('data/{}/{}/{}'.format(row[0],row[1],row[2])) as tekstfile:
                tekst=" ".join([w for w in remove_punctuation(tekstfile.read()).split() if w not in STOPWORDS])
                comparisons[datetoint(row[3])].append((row[1],tekst,row[3],row[2]))
                i+=1
                aantalartikelen[row[1]]+=1
                print('\r{:,} bestanden gelezen'.format(i),end="")
        except:
            print('data/{}/{}/{} kon niet worden gelezen'.format(row[0],row[1],row[2]))
            foutjes+=1
        sys.stdout.flush()


print('\n{} van de {} bestanden konden niet geopend worden'.format(foutjes,i))



with open('output.csv',encoding='utf-8',mode='w') as outputfile:
    writer=csv.writer(outputfile)
    writer.writerow(["from","to","fromdate","todate","fromfile","tofile","fromlength","tolength","levenshtein","cosine"])
    for key in list(comparisons.keys()):
        print("\nWe kijken nu naar {} en de twee voorafgaande dagen.".format(STARTDATE+datetime.timedelta(int(key))))
        if key<=2:
            pass
        else:
            documents = [item for item in comparisons[key]]
            documents = documents + [item for item in comparisons[key-1]]
            documents = documents + [item for item in comparisons[key-2]]
            tfidf = TfidfVectorizer().fit_transform([item[1] for item in documents])
            pairwise_similarity = tfidf * tfidf.T
            cx = sp.sparse.coo_matrix(pairwise_similarity)
            for i,j,v in zip(cx.row, cx.col, cx.data):
                if v>THRESHOLD and datetoint(documents[i][2])<=datetoint(documents[j][2]) and documents[i][0]!=documents[j][0] and documents[i][0]=="ANP":
                    print(documents[i][2]+'-->'+documents[j][2])
                    print(documents[i][0]+'-->'+documents[j][0],':'+str(v)) 
                    #print("SOURCE1: "+documents[i][1][:100])
                    #print("SOURCE2: "+documents[j][1][:100])
                    overlap[documents[i][0]+"_"+documents[j][0]].append(v)
                    overlap2[documents[i][0]+"_"+documents[j][0]]+=1
                    ls=levenshtein(documents[i][1],documents[j][1])
                    overlap3[documents[i][0]+"_"+documents[j][0]].append(ls)
                    writer.writerow([documents[i][0],documents[j][0],documents[i][2],documents[j][2],documents[i][3],documents[j][3],len(documents[i][1].split()),len(documents[j][1].split()),ls,v])


print("\n\n\nSIMILARITY SCORES (gemiddelde van alle scores >{:0.1f}:".format(THRESHOLD))
for key,value in overlap.items():
    print("{}: M={:1.2f}, SD={:1.2f}".format(key,np.mean(value),np.std(value)))



print("\n\n\nLevenshtein distances (gebaseerd op alle paren met een cosine similarity >{:0.1f}:".format(THRESHOLD))
for key,value in overlap3.items():
    print("{}: M={:1.2f}, SD={:1.2f}".format(key,np.mean(value),np.std(value)))



print("\n\n\nAantal overgenomen artikelen:")
for key,value in overlap2.items():
    print("{}\t{}".format(key,value))


print("\n\n\nTotaal aantal artikelen:")
for key,value in aantalartikelen.items():
    print("{}\t{}".format(key,value))
