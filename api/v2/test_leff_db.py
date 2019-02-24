import spacy
import io
import pandas as pd
import psycopg2
from spacy_lefff import LefffLemmatizer, POSTagger

from sqlalchemy import create_engine
from konnect_polen import *
host='localhost:5433'
engine = create_engine('postgresql://'+configuration_db_user_localhost+':'+configuration_db_pass_localhost+'@'+host+'/mehdi.guiraud',encoding='utf-8')



nlp = spacy.load('fr')
pos = POSTagger()
french_lemmatizer = LefffLemmatizer(after_melt=True)
nlp.add_pipe(pos, name='pos', after='parser')
nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')
doc = nlp(u"Paris est une garçon très chère.")
for d in doc:
    print(d.text, d.pos_, d._.melt_tagger, d._.lefff_lemma, d.tag_, d.lemma_)
    texte=[d.text, d.pos_, d._.melt_tagger, d._.lefff_lemma, d.tag_, d.lemma_]
    df_texte=pd.read_csv(io.StringIO(' '.join(texte)))
    df_texte.to_sql('texte',engine, if_exists='replace', index=False)
