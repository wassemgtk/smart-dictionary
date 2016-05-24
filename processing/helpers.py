import re

import BeautifulSoup


def clean_html(document):
    soup = BeautifulSoup.BeautifulSoup(document)
    texts = soup.findAll(text=True)

    def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element)):
            return False
        return True

    visible_texts = filter(visible, texts)

    return '\n'.join(item.strip().encode('utf-8') for item in visible_texts if item.strip())
