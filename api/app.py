from io import StringIO
from nltk.tree import *
from pycorenlp import StanfordCoreNLP
import nltk
import requests
import pandas as pd
import io
from nltk.tree import ParentedTree

# app = Flask(__name__)
from flask_api import FlaskAPI
from flask import request, url_for
# from flask_api import FlaskAPI, status, exceptions
from flasgger import Swagger
from parser import Parser

app = FlaskAPI(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
swagger = Swagger(app)


parser = Parser()
nlp = StanfordCoreNLP('http://localhost:9000')

# @app.route("/parse_sentence/", methods=['GET', 'POST'])
@app.route("/", methods=['GET'])
def parse_sentence():
    if request.method == 'GET':
        # text = str(request.data.get('input', ''))
        text = request.args.get('input')

        parse_output = nlp.annotate(text, properties={
            'annotators': 'tokenize,ssplit,pos,depparse,parse',
            'outputFormat': 'json'
        })

        parsed_sentences = [s['parse'] for s in parse_output['sentences']]

        all_output = ""
        parsed_output = []
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

        all_output = all_output.replace(' .', '. ')

        return {"converted_text": all_output, "parsed_sentences":parsed_output}
    return {"Status": "Fail"}