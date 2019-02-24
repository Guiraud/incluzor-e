#import newspaper
import spacy
from newspaper import Article

url = 'http://www.lefigaro.fr/actualite-france/2019/02/18/01016-20190218ARTFIG00253-l-ecriture-inclusive-face-au-conseil-d-etat.php'
article = Article(url)
article.download()
article.parse()

nlp = spacy.load('fr')
doc = nlp(article.text)
for sent in doc.sents:
    print(sent.text)

#print(article.text)
