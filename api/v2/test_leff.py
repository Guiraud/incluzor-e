import spacy
from spacy_lefff import LefffLemmatizer, POSTagger

nlp = spacy.load('fr')
pos = POSTagger()
french_lemmatizer = LefffLemmatizer(after_melt=True)
nlp.add_pipe(pos, name='pos', after='parser')
nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')
doc = nlp(u"Paris est une garçon très chère.")
for d in doc:
    print(d.text, d.pos_, d._.melt_tagger, d._.lefff_lemma, d.tag_, d.lemma_)
