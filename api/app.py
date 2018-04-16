from flask_api import FlaskAPI
from flask import request
from flasgger import Swagger
from flask_cors import CORS

from parser import Parser
from pycorenlp import StanfordCoreNLP
from io import StringIO
from nltk.tree import Tree
import re

import os
from pymongo import MongoClient
import numpy as np

# Setup Flask
app = FlaskAPI(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Setup Parser
parser = Parser()
nlp = StanfordCoreNLP('http://localhost:9000')

# Connection à mongo
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_client = MongoClient("mongodb+srv://incluzor:{p}@incluzor-1ocjv.mongodb.net/test".format(p=mongo_password))
mongo_db = mongo_client['incluzor']
mongo_col = mongo_db["lexique-validé"]


@app.route("/", methods=['GET'])
def parse_sentence():
    if request.method == 'GET':
        text = request.args.get('input')

        all_output = ""
        parsed_output = []

        # sentences = re.split(r'(\s+)', text)
        # sentences = re.split('.', text)
        # print(sentences)
        # sentences = [text]
        # sentences = text.split(["\n", "."])
        # re.split('\n|,',str)
        sentences = re.split('(\n)', text)
        # sentences = re.split('; |\.|\*|\n', text)
        # sentences = [text]

        for sentence in sentences:
            print("Parse sentence: ", sentence)
            if len(sentence) > 1:
                parse_output = nlp.annotate(sentence, properties={
                    'annotators': 'tokenize,ssplit,pos,depparse,parse',
                    'outputFormat': 'json'
                })

                parsed_sentences = [s['parse'] for s in parse_output['sentences']]

                for parsed_sentence in parsed_sentences:

                    # Get the tree diagram
                    tree_stream = StringIO()
                    Tree.fromstring(parsed_sentence).pretty_print(stream=tree_stream)
                    tree_string = tree_stream.getvalue()

                    converted_sentence = parser.parse(parsed_sentence)
                    parsed_output.append({
                        "parsed": parsed_sentence,
                        "converted": converted_sentence,
                        "tree": tree_string
                        })
                    all_output += converted_sentence
            else:
                all_output += sentence

        all_output = all_output.replace('.', '. ')
        html_output = all_output

        return {"converted_text": all_output, "converted_text_html": html_output, "parsed_sentences": parsed_output}
    return {"Status": "Fail"}


@app.route("/mots/inclusive", methods=['GET'])
def get_inclusive():
    """ Trouver la liste des mots inclusives """

    # Paramètre: Le mot à retourner
    mot_masc = request.args.get('masc')
    mot_masc = re.split(' ', mot_masc)[0]

    # Trouver les versions inclusives
    res = mongo_col.find_one({"$or": [{"masc_sing": mot_masc},
                             {"masc_plur": mot_masc}]})
    res_erreur = None

    if res is None:
        res = None
        res_erreur = "Mot pas trouvé."
    else:
        res.pop("_id")
        ajoute_frequence_proportionelle(res["feminines"])
        nettoyer_resultats(res["feminines"])

    # Return un objet json.
    output = {"mot_requete": mot_masc, "inclusives": res, "erreur": res_erreur}
    return output


def nettoyer_resultats(versions_fem):
    """ nettoyer la colonne 'note'  """
    for version in versions_fem:
        if np.isnan(version["note"]):
            version["note"] = None


def ajoute_frequence_proportionelle(versions_fem):
    """ Fréquence des mots féminins. Pour le moment nous resons sur
        les mots féminins car nous n'avons pas des calculs de la fréquence
        des versions iclusives ou au neutre. """

    # Fréquence totale
    total_freq = 0
    for version in versions_fem:
        total_freq = total_freq + version["count"]

    # Calcule les fréquence proportionelle de chaque version
    for version in versions_fem:
        version["rating"] = version["count"] / total_freq


@app.route("/mots/index", methods=['GET'])
def get_mots():
    """ Trouver la liste de mots (masculins) """

    # Paramètre: Les lettres du début des mots à retourner
    prefix_text = request.args.get('q')

    if prefix_text == None:
        prefix_text = ""

    # Trouver les mots dans mongo qui commence avec ces lettres.
    # TODO: changer ça à quelque chose plus efficace
    regx = re.compile("^"+prefix_text, re.IGNORECASE)
    output = mongo_col.distinct("masc_sing", {"masc_sing": regx})

    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5005)
