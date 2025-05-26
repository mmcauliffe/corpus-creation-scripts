import itertools
import os

import wikipron
import unicodedata
import re
import requests_html
import lxml
import pkg_resources
import requests
import segments
import time
import json
import functools
output_file = r'backup_dictionaries/japanese.tsv'

languages = ['Japanese']

_CATEGORY_TEMPLATE = "Category:{language} terms with IPA pronunciation"
# Http headers for api call
HTTP_HEADERS = {
    "User-Agent": (
        f"Montreal-Forced-Aligner/2.1.0"
        "(https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) "
        f"requests/{requests.__version__}"
    ),
}
_PAGE_TEMPLATE = "https://en.wiktionary.org/wiki/{word}"

def _skip_word(word: str, skip_spaces: bool) -> bool:
    # Skips reconstructions.
    if word.startswith("*"):
        return True
    # Skips multiword examples.
    if skip_spaces and (" " in word or "\u00A0" in word):
        return True
    # Skips examples containing a dash.
    if "-" in word:
        return True
    # Skips examples containing digits.
    if re.search(r"\d", word):
        return True
    return False

cleanup_characters = {'ᵝ', '͡','̠', '̞', '̟', '̃'}

def process_pronunciation(pron: str):
    pron = pron.strip()[1:-1]
    pron = unicodedata.normalize("NFD", pron)
    pron = segments.Tokenizer()(pron, ipa=True).replace(' #', '')
    for c in cleanup_characters:
        pron = pron.replace(c, '')
    return pron

IPA_XPATH_SELECTOR = '//span[@class = "IPA"]'
LANGUAGE_SELECTOR = '//h2[span = "{language}"]'

pos_sections = {'Verb', 'Adjective', 'Proper noun', 'Adnominal',
                'Noun', 'Pronoun', 'Adverb','Interjection', 'Particle', 'Numeral', 'Counter', 'Conjunction'}
morphological_sections = {'Suffix', 'Prefix',}

def _scrape_word(word:str):
    session = requests_html.HTMLSession()
    request = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    words = request.html.xpath('//strong[@class = "Deva headword"]')

    urdu_words = []
    for w in words:
        if w.text.strip() != word:
            continue
        elements = w.element.getparent().xpath('//b[@lang="ur"]')
        if not elements:
            continue
        urdu_words.extend([x.text_content() for x in elements])
    return sorted(set(urdu_words))


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

hindi_dictionary_path = r"D:\Data\speech\dictionaries\wikipron\cleaned\hindi.txt"
urdu_dictionary_path = r"D:\Data\speech\dictionaries\wikipron\cleaned\urdu.txt"

if __name__ == '__main__':

    RESTART_KEY = None
    with open(hindi_dictionary_path, 'r', encoding='utf8') as inf, open(urdu_dictionary_path, 'w', encoding='utf8') as outf:
        for line in inf:
            line = line.strip()
            if not line:
                continue
            word, pron = line.split(maxsplit=1)
            print(word)

            urdu_words = _scrape_word(word)
            if not urdu_words:
                continue
            print(word, urdu_words, pron)
            for urdu_word in urdu_words:
                outf.write(f"{urdu_word}\t{pron}\n")