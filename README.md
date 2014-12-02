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

###csv2gdf

A Python script that takes a CSV file and converts it to a GDF file. It is typically used to process CSV files that contain Twitter data (e.g., collected by yourTwapperkeeper), but one could imagine other applications as well.
It allows different types of networks to be constructed:
(1) Word co-occurrences (which words are often used together). This module also produces a frequency table of each words.
(2) Interaction networks, like networks of @mentions, @replies or retweets.


```
usage: csv2gdf.py [-h] [--column COLUMN] [--sendercolumn SENDERCOLUMN]
                  [--cutoff CUTOFF] [--minedgeweight MINEDGEWEIGHT]
                  [--stopwordfile STOPWORDFILE] [--retweet] [--reply]
                  [--allinteractions] [--cooccurrences]
                  [filename]

This program creates GDF network files based on input data in CSV format.

positional arguments:
  filename              The file you want to analyze. If you don't provide a
                        filename, we'll read from STDIN

optional arguments:
  -h, --help            show this help message and exit
  --column COLUMN       In which column of the CSV file is the data you want
                        to analyse. We start counting with 0, so the second
                        column is called 1. If not provided, we use column 0.
  --sendercolumn SENDERCOLUMN
                        In which column of the CSV file is the SENDER (only
                        for mention and retweet networks). We start counting
                        with 0, so the second column is called 1. If not
                        provided, we use column 2.
  --cutoff CUTOFF       Define a cutoff percentage: The least frequently used
                        x procent are not included. Write 0.1 for 10 per cent.
                        If not provided, we use 0 and thus include all
                        elements.
  --minedgeweight MINEDGEWEIGHT
                        Define a minimum edgeweight and discard less frequent
                        coooccurrences.
  --stopwordfile STOPWORDFILE
                        A file with stopwords (i.e., words you want to ignore)
  --retweet             Produces a retweet network
  --reply               Produces a mention network
  --allinteractions     Produces a network that does not distinguish between
                        RT, mention, Reply
  --cooccurrences       Procudes a GDF-file with word-cooccurrences
```

### lnparse.py

Very first draft of a script to parse LexisNexis output. 


### lnsentiment.py

Conducts a sentiment analysis of folders with lexis nexis articles



### nutop5.py

This program parses the information provided in the "Meest gelezen" (most read) section on the homepage of the Dutch news site nu.nl. It can access nu.nl directly, or process a folder with previously saved copies of the nu.nl homepage. It writes the output to a file named output.csv, containing URL, title, and position on the Top 5-ranking of the article.


```
usage: nutop5.py [-h] [--live] [folder]

This program parses the top 5 most read articles from nu.nl. As input, it
takes either a folder of saved nu.nl-homepages or it looks up the top 5 at
this moment.

positional arguments:
  folder      In which folder are the saved nu.nl-homepages

optional arguments:
  -h, --help  show this help message and exit
  --live      Look at the top 5 right now instead of analyzing saved homepages
```

### nutextparse.py

This program seperates the text body of articles from nu.nl from the rest, stripping all navigation elements and the like. It saves the headline, the publication and update dates, and the text itself to text files.

```
usage: nutextparse.py /path/to/folder/with/articles

```


### rsshond

RSShond checks RSS feeds (typically feeds of news sites), makes a CSV table with all relevant data, and additionally downloads the full articles. Put RSS-feeds into `sources.conf`. Use cron or a similar program to start RSShond regularly (for example, once an hour). 
It requires the Python module "feedparser" to be installed (`pip install feedparser`).