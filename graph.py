import networkx as nx
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import ssl

from openie import StanfordOpenIE

class KnowledgeGraph:
    def __init__(self, context: str):
        self.context = context

        self.ner_model = spacy.load("en_core_web_lg")
        doc = self.ner_model(self.context)
        self.entities = [(ent.text, ent.label_) for ent in doc.ents]

        self.graph = nx.Graph()

    def get_entity_set(self):
        return set([text for text, _ in self.entities])

    def extract_relations(self):
        ssl._create_default_https_context = ssl._create_unverified_context

        relations = []
        with StanfordOpenIE() as client:
            for triple in client.annotate(self.context):
                relations.append(triple)
        return relations

if __name__ == "__main__":
    with open("context.txt", "r") as file:
        context = file.read()
    kg = KnowledgeGraph(context)
    print(f'Entities are: {kg.entities}')
    print(f'Relations are: {kg.extract_relations()}')
