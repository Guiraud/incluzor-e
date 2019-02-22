import spacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('fr_core_news_sm')

# Process whole documents
text = (u"Dénigrée par le gouvernement, on la croyait marginalisée. Cantonnée à un petit groupe de militants jusqu'au-boutistes, voués à disparaître avec le temps. «J'ai du mal à lire et je trouve ça un peu couillon»déclarait Christophe Castaner à propos de l'écriture «inclusive», tandis qu'Édouard Philippe donnait consigne à ses ministres de la bannir des textes administratifs. En sifflant la fin de ce militantisme orthographique, le gouvernement pensait de bonne foi mettre un terme à une dérive un peu trop visible. C'était sans compter l'habileté de ceux qui la portent et qui voient dans notre grammaire la marque de la domination masculine. Sans compter non plus le chemin parcouru. Un an plus tard, si le point médian à bien disparu, l'obsession linguistique du féminin est toujours plus présente.")
doc = nlp(text)

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)
