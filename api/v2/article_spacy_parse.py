#import newspaper
import spacy
from newspaper import Article
from spacy import displacy
import pandas as pd
import datetime
import time
import psycopg2
import io
from spacy_lefff import LefffLemmatizer, POSTagger
from sqlalchemy import create_engine
from konnect_polen import *

def init_bdd():
	"""
	Initialiser la base de données et une variable qui servira d'index
	"""	
	host='localhost:5433'
	engine = create_engine('postgresql://'+configuration_db_user_localhost+':'+configuration_db_pass_localhost+'@'+host+'/mehdi.guiraud',encoding='utf-8')
	return engine

def get_article(url='http://www.lefigaro.fr/actualite-france/2019/02/18/01016-20190218ARTFIG00253-l-ecriture-inclusive-face-au-conseil-d-etat.php'):
	"""
	récupération d'un texte martyr
	"""
	article = Article(url)
	article.download()
	article.parse()
	return article.text

def init_spacy():
	"""
	Initialiser avec la langue française et la lemmisation Leff (spacy-leff)
	"""
	nlp = spacy.load('fr')
	pos = POSTagger()
	french_lemmatizer = LefffLemmatizer(after_melt=True)
	nlp.add_pipe(pos, name='pos', after='parser')
	nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')
	return nlp

def find_subject(doc):
	"""
	Trouver le ou les sujets dans un groupe de phrase
	"""
	for chunk in doc.noun_chunks:
		print(chunk.text, chunk.label_, chunk.root.text)


def divide_sentences(texte):
	"""
	Diviser un paragraphe en plusieurs phrases pour un traitement ultérieur.
	/!\  Cela n'est pas forcément correct puisqu'une phrase peut avoir un sujet dans une autre phrase /!\
	- Ajouter une gestion des exceptions
	"""

	if len(texte) > 0:
		nlp = spacy.load('fr')
		doc = nlp(texte)
		init_spacy()
		for sent in doc.sents:
			print(sent.text)
			find_subject(sent)
			detect_incoherence(sent)

	else:
		print("texte vide")

def noun_gender(tag):
	"""
	fonction locale qui permet de detecter si un mot est masculin ou féminin
	"""
	if 'Fem' in tag:
		return 'Fem'
	elif 'Masc' in tag:
		return 'Masc'
	else:
		return None		

def send_bdd_words(token,engine):
	"""
	Envoie en base de données chaque mot et sa définition "Leff". 	 : 
	"""
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	df_texte=pd.DataFrame({'timestamp':pd.Timestamp(st),'text':token.text,'pos_':token.pos_,'melt_tagger':token._.melt_tagger,'lefff_lemma':token._.lefff_lemma,'tag_':token.tag_,'lemma_':token.lemma,'dep_':token.dep_}, index=[0])
	df_texte.to_sql('phrase',engine, if_exists='append', index=False)

def detect_incoherence(doc):
	"""
	Signale si il existe une incohérence de genre entre un mot et son "sujet" 
	"""
	for token in doc:
		a = [token.head.tag_,token.tag_]
		if any("Fem" in s for s in a) and any("Masc" in s for s in a):
			print("Détection : {0}({1}) <--{2}({3})".format(token.tag_,noun_gender(token.tag_), token.head.tag_,noun_gender(token.head.tag_)))
			print("{0}/{1}({2}) <--{3}-- {4}/{5} \n============================\n".format(token.text, token.tag_,token._.lefff_lemma, token.dep_, token.head.text, token.head.tag_))


if __name__ == "__main__":
	"""
	Récupère un article, le découpe en phrase et signale les incohérence de genre.
	"""

	print("Récupération du texte martyr")
	texte = get_article()
	divide_sentences(texte)
