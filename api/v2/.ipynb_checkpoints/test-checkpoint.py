import spacy
from spacy import displacy
nlp = spacy.load('fr')
doc = nlp(u'Ceci est une phrase.')
print([(w.text, w.pos_) for w in doc])
displacy.serve(doc, style='dep')
