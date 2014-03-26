#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

bestandsnaam="De_Telegraaf2014-03-22_22-08.TXT"

artikel=0
tekst={}
datum={}
section={}
length={}
loaddate={}
language={}
pubtype={}
journal={}

with open(bestandsnaam,"r") as f:
	for line in f:
		line=line.replace("\r","")
		if line=="\n":
			continue
		matchObj=re.match(r"\s+(\d+) of (\d+) DOCUMENTS",line)
		if matchObj:
			# print matchObj.group(1), "of", matchObj.group(2)
			artikel= int(matchObj.group(1))
			#artikel+=1
			tekst[artikel]=""
			continue
		if line.startswith("SECTION"):
			section[artikel]=line.replace("SECTION: ","").rstrip("\n")
		elif line.startswith("LENGTH"):
			length[artikel]=line.replace("LENGTH: ","").rstrip("\n")
		elif line.startswith("LOAD-DATE"):
			loaddate[artikel]=line.replace("LOAD-DATE: ","").rstrip("\n")
		elif line.startswith("LANGUAGE"):
			language[artikel]=line.replace("LANGUAGE: ","").rstrip("\n")
		elif line.startswith("PUBLICATION-TYPE"):
			pubtype[artikel]=line.replace("PUBLICATION-TYPE: ","").rstrip("\n")
		elif line.startswith("JOURNAL-CODE"):
			journal[artikel]=line.replace("JOURNAL-CODE: ","").rstrip("\n")
		elif line.lstrip().startswith("Copyright "):
			pass
		elif line.lstrip().startswith("All Rights Reserved"):
			pass
		else:
			tekst[artikel]=tekst[artikel]+line
		
		