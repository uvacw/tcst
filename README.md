# The Communication Scientist's Toolbox

The Communication Scientist's Toolbox is a collection of scripts that might help you to analyze and collect data. The aim is to provide students and researchers with the tools they need to conduct Communication Science methods like content analysis or network analysis in a digital environment. It is a toolbox, not a ready-made suite of programs. That means that you have to assemble the building blocks yourself - installers and pretty user interfaces don't have priority. The nice thing: Because of this, you have many possibilities to modify the code so that it fits your needs. And, if your dataset grows too big, nothing stops you from running the code on a powerful server. Ever tried something like that with a point-and-click program?

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

A Python script that takes files produced by [netvizz](http://apps.facebook.com/netvizz) and analyzes them. Currently, it only takes files from Facebook pages (i.e., not groups), but it should be easy to modify it accordingly. It gives you statistics like M, SD, min, max, skewness, kurtosis of the number of comments, likes, posts, ...  
It furthermore analyzes the length of messages, the most frequently used words, and can produce a network-file for visualization of the word cooccurences. 

```
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
```

### filterfolder.py

A Python script that takes a folder of your choice (e.g. "c:\myarticles" or "/home/damian/mijnartikelen") and a [regular expression](http://en.wikipedia.org/wiki/Regular_expression) as input and produces a CSV-table in which it counts how often the regular expression is used in each article. This is very useful for filtering: Imagine you have a folder with 10.000 articles (they are assumed to be in plain text format, but you might be able to abuse the program for other formats) and you want to have a look at only those that are on a specific topic, then you can use the output to see which ones that are.

```
usage: filterfolder.py [-h] folder regexp

This program creates a CSV table in which it counts houw often a specific
regular expressions occurs in each file in a folder.

positional arguments:
  folder      The folder you want to analyze. The program assumes each file in
              the folder to be a plain text file.
  regexp      The regular expression you want to search for

optional arguments:
  -h, --help  show this help message and exit

```
