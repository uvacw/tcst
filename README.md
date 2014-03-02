# The Communication Scientist's Toolbox

The Communication Scientist's Toolbox is a collection of scripts that might help you to analyze and collect data. The aim is to provide students and researchers with the tools they need to conduct Communication Science methods like content analysis or network analysis in a digital environment. It is a toolbox, not a ready-made suite of programs. That means that you have to assemble the building blocks yourself - there is no installer and no user interface, but many possibilities to modify the code so that it fits your needs.

The toolbox is work in progress, and you are more than welcome to contribute. I hope to hear from you!

Damian  
@damian0604

Dr. Damian Trilling  
Lecturer Political Communication and Journalism  
University of Amsterdam  
www.damiantrilling.net  


##  What do I need?

[Python](www.python.org). The scripts are written in Python 2.7. Some scripts will run with older versions, but they are not compatible with Python 3. Some scripts need additional Packages like [numpy](www.numpy.org), [scipy](www.scipy.org), [NLTK](www.nltk.org) or [Pattern](www.clips.ua.ac.be/pattern).


## How can I learn all this?

First of all, if you are a student, you can enroll in my Research Master Course on Big Data and automated content anylsis at the Graduate School of Communication at the University of Amsterdam. You can also have a look at my tutorial [Python for Communication Scientists](www.damiantrilling.net/downloads/py_for_cs.pdf).  

## What does the toolbox contain?

### vizzstat.py

A Python script that takes files produced by [netvizz](http://apps.facebook.com/netvizz) and analyzes them. It gives you statistics like M, SD, min, max, skewness, kurtosis of the number of comments, likes, posts, ...  
It furthermore analyzes the length of messages, the most frequently used words, and can produce a network-file for visualization of the word cooccurences. 


usage: vizzstat.py [-h] [--descriptives] [--content] [--cooccurrences]
                   filename {a,b,c}

This program creates a report with summary statistics of Facebook data. As
input, it takes files created py the "page data" function provided by netvizz
(apps.facebook.com/netvizz)

positional arguments:
  filename         The file you want to analyze
  {a,b,c}          a b or c - the file type as provided by netvizz: (a)
                   bipartite graph file in gdf format that shows posts, users,
                   and connections between the two; (b) tabular file (tsv)
                   that lists different metrics for each post; (c) tabular
                   file (tsv) that contains the text of user comments (users
                   anonymized).

optional arguments:
  -h, --help       show this help message and exit
  --descriptives   Provides general descriptive statistics
  --content        Analyzes the content and provides statistics like the
                   average message length or the most frequently used words
  --cooccurrences  Equal to --content, but in addition, it procudes a GDF-file
                   with word-cooccurrences
