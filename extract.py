# -*-coding:utf-8 -*
import sys
import nltk
import requests
from lxml import html
from lxml import etree
from StringIO import StringIO
from csv import DictWriter
from nltk.tokenize import word_tokenize

lien = sys.argv[1]

#f= StringIO('<a href="http://www.lefigaro.fr/flash-actu/2018/01/07/97001-20180107FILWWW00094-val-d-oise-un-controle-de-police-degenere.php">')
#page = requests.get('http://www.lefigaro.fr/flash-actu/2018/01/07/97001-20180107FILWWW00094-val-d-oise-un-controle-de-police-degenere.php')
page = requests.get(lien)

f = html.fromstring(page.content)
#doc = etree.parse(f)

data=[]
# Get all links with data-spm-anchor-id="0.0.0.0" 
r = f.xpath('/html/body/div[3]/div/div[1]/div[1]/article/div[2]/p/text()')

# Iterate thru each element containing an <a></a> tag element
for elem in r:
    text = u''.join(elem).encode('utf-8').strip().replace('\xc2\xa0','')
    print str(len(text))+"===>"+text
    for i in r:
	text_inclu=word_tokenize(i, language='french')
	print(text_inclu)
    data.append({
        #'link': link,
        #'title': title,
        #'text': text
	'': text_inclu
    })

with open('file.csv', 'w') as csvfile:
    #fieldnames=['link', 'title', 'text']
    fieldnames=['']
    writer = DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
