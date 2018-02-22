from pycorenlp import StanfordCoreNLP
import nltk
import requests
import pandas as pd
import io
from nltk.tree import ParentedTree


class Parser():
    def __init__(self):
        self.setup_parser()

    def load_csv_url(self, url, sep=","):
        s = requests.get(url).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')), sep=sep)
        return df

    def setup_parser(self):
        # liste des noms
        self.noms_liste = self.load_csv_url("http://test.incluzor.fr/data/lexique_numerique_fusion_guy.tsv", sep="\t")
        self.noms_liste["ignore"] = ""
        # lists des régularités des adjectifs
        self.adjectifs_reg = self.load_csv_url("http://test.incluzor.fr/data/adjectivesv-0.1.csv")

        # liste des adjectifs
        self.adjectifs_liste = self.load_csv_url("http://test.incluzor.fr/data/adjectivesv-0.1.csv")

        self.determinants_liste = self.load_csv_url("http://test.incluzor.fr/data/determinants-v0.1.csv", sep=";")

    def tag_parent(self, tree, plural):
        parent = tree.parent()
        if parent.label() == "NP":
            if plural:
                parent.set_label("NP-BiPlur")
            else:
                parent.set_label("NP-BiSing")

    def find_nc(self, tree):
        if tree.height() == 2:
        # TODO handle case of both sing and plur
        # TODO handle PRO as their own thing
        #      see: https://fr.wikipedia.org/wiki/Pronom_ind%C3%A9fini#Le_pronom_%C2%AB_nul_%C2%BB
            if tree.label() == "NC" or tree.label() == "PRO":
                word = tree[0].lower().strip()

                # CHECK FOR SINGULAR
                noun_matches = self.noms_liste[(self.noms_liste["Masc Singulier"] == word) & (self.noms_liste["ignore"] != "x")]

                if noun_matches.shape[0] > 1:
                    raise Exception("noun_matches.shape[0] > 1")
                elif noun_matches.shape[0] > 0:
                    if noun_matches["Masc Singulier"].iloc[0] == noun_matches["Fem Singulier"].iloc[0]:
                        forme_bigenre = noun_matches["Masc Singulier"].iloc[0]
                    else:
                        forme_bigenre = noun_matches["Incl sing V1"].iloc[0]

                    self.tag_parent(tree, False)
                    tree.__setitem__(0, forme_bigenre)

                # CHECK FOR PLURAL
                noun_matches = self.noms_liste[(self.noms_liste["Masc Pluriel"] == word) & (self.noms_liste["ignore"] != "x")]

                if noun_matches.shape[0] > 1:
                    raise Exception("noun_matches.shape[0] > 1")
                elif noun_matches.shape[0] > 0:
                    if noun_matches["Masc Pluriel"].iloc[0] == noun_matches["Fem Pluriel"].iloc[0]:
                        forme_bigenre = noun_matches["Masc Pluriel"].iloc[0]
                    else:
                        forme_bigenre = noun_matches["Incl pl V1"].iloc[0]

                    self.tag_parent(tree, True)
                    tree.__setitem__(0, forme_bigenre)

        for subtree in tree:
            if type(subtree) == nltk.tree.ParentedTree:
                self.find_nc(subtree)

    def replace_det(self, det, plural):
        try:
            return self.determinants_liste[self.determinants_liste["masc"] == det]["bigenre"].iloc[0]
        except:
            return "[DET]"

    def replace_adj(self, adj, plural):
        for idx, row in self.adjectifs_reg.iterrows():
            if plural:
                masc_ending = row["masc_plur"]
            else:
                masc_ending = row["masc_sing"]

            if adj.endswith(masc_ending):
                out_adj = adj[0:len(adj) - len(masc_ending)]
                out_adj += row.get("inc_plur").lower().strip()
                return out_adj

        return out_adj

    def replace_accords(self, tree, inclusive, plural):
        if tree.label() == "NP-BiSing":
            inclusive = True
            plural = False

        if tree.label() == "NP-BiPlur":
            inclusive = True
            plural = True

        if inclusive:
            if tree.label() == "ADJ":
                tree.__setitem__(0, self.replace_adj(tree[0].lower().strip(), plural))
            if tree.label() == "DET":
                tree.__setitem__(0, self.replace_det(tree[0].lower().strip(), plural))
            # if tree.label() == "P":
            #     tree.__setitem__(0, self.replace_det(tree[0].lower().strip(), plural))

        for subtree in tree:
            if type(subtree) == nltk.tree.ParentedTree:
                self.replace_accords(subtree, inclusive, plural)

    def parse(self, sentence):

        sentence = ParentedTree.fromstring(sentence)

        sentence.pretty_print()

        self.find_nc(sentence)
        self.replace_accords(sentence, False, False)

        sentence.pretty_print()

        out = " ".join(sentence.leaves())

        return out
