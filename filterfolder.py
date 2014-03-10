#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is filterfolder, a program to count words in a folder with text files.
# Copyright (C) 2014 DAMIAN TRILLING
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact me via d dot c dot trilling at uva dot nl

import csv
import codecs
import re
import sys
import os
from os import listdir
from os.path import isfile, join
import argparse

print "filterfolder 0.1 Copyright (C) 2014  Damian Trilling"
print "This program comes with ABSOLUTELY NO WARRANTY."
print "This is free software, and you are welcome to redistribute it under certain conditions; read the file LICENSE which you received with this program."
print "\n"


parser=argparse.ArgumentParser(description='This program creates a CSV table in which it counts houw often a specific regular expressions occurs in each file in a folder.')
parser.add_argument("folder", help="The folder you want to analyze. The program assumes each file in the folder to be a plain text file.")
parser.add_argument("regexp", help="The regular expression you want to search for")

args=parser.parse_args()

mypath =args.folder                     # in welke map zitten de artikelen? (relatief!)
outputbestand="overzichtstabel.csv"     # waar de output opslaan?
regex1 = re.compile(args.regexp)        # waarop zoeken?

filename_list=[]
matchcount1=0
matchcount1_list=[]

print "\nWelkom. Er zal in de map "+mypath +"worden gezocht op de uitdrukking \""+regex1.pattern

onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for f in onlyfiles:
	matchcount1=0
	artikel=open(join(mypath,f),"r")
	for line in artikel:
		matches1 = regex1.findall(line)
		for word in matches1:
			matchcount1=matchcount1+1
		print '\"' + regex1.pattern + '\" is ' + str(matchcount1) + ' keer gevonden in ' + join(mypath,f)
	filename_list.append(f)
	matchcount1_list.append(matchcount1)
	artikel.close()
output=zip(filename_list,matchcount1_list)
writer = csv.writer(open(outputbestand, 'wb'))
writer.writerows(output)
print "\nWe zijn klaar! De output staat in het bestand "+outputbestand+".\n"