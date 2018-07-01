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

from sqlalchemy import create_engine
import pandas as pd
import unidecode

import requests
from bs4 import BeautifulSoup

# Setup Flask
app = FlaskAPI(__name__)
app.config.from_object('default_settings')
print(app.config["MONGO_STRING"])

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Setup Parser
parser = Parser()
nlp = StanfordCoreNLP('http://localhost:9000')

# Connection à mongo
# mongo_password = os.environ.get('MONGO_PASSWORD')
# mongo_string = app.config["PSQL_STRING"]
# mongo_client = MongoClient("mongodb+srv://incluzor:{p}@incluzor-1ocjv.mongodb.net/test".format(p=mongo_password))
# mongo_db = mongo_client['incluzor']
# mongo_col = mongo_db["lexique-validé"]

psql_string = app.config["PSQL_STRING"]
psql_engine = create_engine(psql_string)


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
    """ Trouver la liste de mots inclusifs """

    # Paramètre: Le mot à retourner
    mot_masc = request.args.get('masc')
    mot_masc = re.split(' ', mot_masc)[0]

    # Trouver les versions inclusives
    res = mongo_col.find_one({"$or": [{"masc_sing": mot_masc},
                             {"masc_plur": mot_masc}]})
    res_erreur = None
    print(res)

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
        if type(version["note"]) == float:
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


@app.route("/mots/fréquence", methods=['GET'])
def get_freq():

    word = request.args.get('q')

    output = {}
    if type(word) == str:
        ngrams = pd.read_sql("select * from ngrams{l} where word = '{w}';".format(l=unidecode.unidecode(word[0]), w=word), engine)
        output["ngrams"] = (int)(ngrams["year"].sum())

    return output


@app.route("/mots/dict", methods=['GET'])
def check_dict():
    mot = request.args.get('mot')
    dictionnaire = request.args.get('dictionnaire')

    print(dictionnaire)

    if dictionnaire == "cnrtl":
        output = scrape_cnrtl(mot)
    if dictionnaire == "larousse":
        output = scrape_larousse(mot)
    if dictionnaire == "littré":
        output = scrape_littré(mot)
    # if dictionnaire == "reverso":
    #     output = scrape_reverso(mot)
    if dictionnaire == "wiktionnaire":
        output = get_wiktionnaire(mot)
    if dictionnaire == "olfq":
        output = get_olfq(mot)
    if dictionnaire == "lefff":
        output = get_lefff(mot)
    if dictionnaire == "dicollecte":
        output = get_dicollecte(mot)

    return {"existe": output}


def scrape_cnrtl(mot):
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    r = requests.get('http://www.cnrtl.fr/definition/'+mot, proxies=proxies)

    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find(id="contentbox")
    if content:
        if "ErreurCette forme est introuvable !" in content.getText():
            return False
        elif "Terme introuvable" in content.getText():
            return False
        else:
            return True
    else:
        raise Exception("'Contentbox' pas trouvé")


def scrape_larousse(mot):
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    r = requests.get('http://www.larousse.fr/dictionnaires/francais/' + mot, proxies=proxies)

    soup = BeautifulSoup(r.text, 'html.parser')
    if soup.find(class_="corrector"):
        return False
    if soup.find(class_="BlocDefinition"):
        return True
    else:
        raise Exception("'Contentbox' pas trouvé")


def scrape_littré(mot):
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    r = requests.get('https://www.littre.org/definition/'+mot, proxies=proxies)

    soup = BeautifulSoup(r.text, 'html.parser')

    if soup.find(class_="definition"):
        return True
    if "Mot " + mot + " non trouvé" in soup.find(id="main-content").getText():
        return False


# def scrape_reverso(mot):
#     proxies = {
#         'http': 'socks5://127.0.0.1:9050',
#         'https': 'socks5://127.0.0.1:9050'
#     }
#     r = requests.get('https://dictionary.reverso.net/french-definition/'+mot, proxies=proxies)

#     soup = BeautifulSoup(r.text, 'html.parser')

#     if soup.find(class_="tNotFound"):
#         return False
#     if soup.find(class_="tNotFound"): #         return False

def get_wiktionnaire(mot):
    raise Exception("Not implemented")


def get_olfq(mot):
    res = pd.read_sql("select * from lexique_olfq where \"Masculin\" = '{w}' or \"Féminin\" = '{w}';".format(w=lower(mot)), psql_engine)
    if(res.shape[0] != 0):
        return True
    return False


def get_lefff(mot):
    res = pd.read_sql("select * from lexique_lefff where lower(\"flexion\") = '{w}';".format(w=lower(mot)), psql_engine)
    if(res.shape[0] != 0):
        return True
    return False


def get_dicollecte(mot):
    res = pd.read_sql("select * from lexique_dicollecte where lower(\"Flexion\") = '{w}';".format(w=mot), psql_engine)
    if(res.shape[0] != 0):
        return True
    return False


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5005)
