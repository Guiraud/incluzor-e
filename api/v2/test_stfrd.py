import stanfordnlp
#stanfordnlp.download('fr_spoken')   # This downloads the English models for the neural pipeline
nlp = stanfordnlp.Pipeline(lang='fr', treebank='fr_spoken') # This sets up a default neural pipeline in English
doc = nlp("La Femme naît libre et demeure égale à l'homme en droits.")
#doc.sentences[0].print_dependencies()
dep_parser = CoreNLPDependencyParser(url='http://localhost:9000')
parse, = dep_parser.raw_parse('La Femme naît libre et demeure égale à l\'homme en droits.')
print(parse.to_conll(4))
