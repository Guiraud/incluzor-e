from flask_api import FlaskAPI
from flask import request
from flasgger import Swagger
from flask_cors import CORS

from parser import Parser
from pycorenlp import StanfordCoreNLP
from io import StringIO
from nltk.tree import Tree
import re

# Setup Flask
app = FlaskAPI(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Setup Parser
parser = Parser()
nlp = StanfordCoreNLP('http://localhost:9000')

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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5005)
