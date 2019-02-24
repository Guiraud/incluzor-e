import pandas as pd
import stanfordnlp

stanfordnlp.download('fr')

nlp = stanfordnlp.Pipeline(processors = "tokenize,mwt,lemma,pos")
doc = nlp("En histoire, et dans les sciences sociales, la situation est consternante : chute inexorable du nombre de postes, des milliers de jeunes docteur.e.s sur le carreau qui survivent de vacations rendues nécessaires par les millions d'heures de cours non pourvues... nous sombrons !")

doc.sentences[0].print_tokens()

def extract_lemma(doc):
    parsed_text = {'word':[], 'lemma':[]}
    for sent in doc.sentences:
        for wrd in sent.words:
            #extract text and lemma
            parsed_text['word'].append(wrd.text)
            parsed_text['lemma'].append(wrd.lemma)
    #return a dataframe
    return pd.DataFrame(parsed_text)

#call the function on doc
extract_lemma(doc)
