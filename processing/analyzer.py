import sys
import os


mitie_location = os.path.join(os.path.dirname(__file__), 'mitie-v0.2-python-2.7-windows-or-linux64')
sys.path.append(mitie_location)


from mitie import tokenize
from mitie import named_entity_extractor
from helpers import clean_html


def parse_document(document, information):
    print 'Acquiring extractor'
    extractor = named_entity_extractor(os.path.join(mitie_location, 'MITIE-models/english/ner_model.dat'))

    print 'Cleaning HTML'
    cleaned_document = clean_html(document)

    print 'Tokenizing'
    tokens = filter(None, tokenize(cleaned_document))

    print 'Extracting NER Entities'
    entities = extractor.extract_entities(tokens)

    print 'Done'
    normalizes_entities = []

    for position, tag in entities:
        position_indices = list(position)
        # TODO: join how for other languages?
        words = ' '.join(tokens[position_indices[0]:position_indices[-1]])
        if words:
            normalizes_entities.append((tag, words))

    return normalizes_entities


def demo():
    import requests

    response = requests.get('http://time.com/3143745/isis-iraq-airstrikes-obama/')
    response.raise_for_status()
    relevant_words = parse_document(response.content, {'url': 'http://time.com/3143745/isis-iraq-airstrikes-obama/'})
    print relevant_words


if __name__ == '__main__':
    demo()
