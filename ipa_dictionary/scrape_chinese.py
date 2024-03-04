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
import jsonlines
import json
import functools
output_file = r'backup_dictionaries/japanese.tsv'

languages = ['Chinese']

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

dialect_to_langauge_mapping = {
    'Teochew': 'Min Nan'
}

def _scrape_word(word:str):
    session = requests_html.HTMLSession()
    request = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    word_data = {'word': word, 'languages': {}}
    pron_panels = request.html.xpath('//div[contains(@class, "zhpron")]')
    for panel in pron_panels:
        pronunciations = panel.xpath('//span[@class = "IPA"]')
        for p in pronunciations:
            prons = [process_pronunciation(x) for x in p.text.split(",")]
            try:
                dialect = p.element.getparent().getparent().getparent().find('small').text_content()[1:-1]
            except:
                continue
            try:
                language = p.element.getparent().getparent().getparent().getparent().getparent().find('a').text_content()
            except:
                pass
            if language not in word_data['languages']:
                word_data['languages'][language] = {}
            if dialect not in word_data['languages'][language]:
                word_data['languages'][language][dialect] = set()
            word_data['languages'][language][dialect].update(prons)


    return word_data

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def scrape():
    """Scrapes with a given configuration."""
    global RESTART_KEY
    category = _CATEGORY_TEMPLATE.format(
        language=languages[0]
    )
    print(category)
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "500",
        "cmprop": "ids|title|timestamp|sortkey",
    }
    if RESTART_KEY is not None:
        requests_params.update({"cmstarthexsortkey": RESTART_KEY})
    with open('rich_lexicons/chinese.jsonl', 'a', encoding='utf8') as word_f:
        word_writer = jsonlines.Writer(word_f, dumps=functools.partial(json.dumps, default=set_default, ensure_ascii=False))
        while True:
            data = requests.get(
                "https://en.wiktionary.org/w/api.php?",
                params=requests_params,
                headers=HTTP_HEADERS,
            ).json()
            #print(f"Processing {requests_params['sroffset']} of {data['query']['searchinfo']['totalhits']}")
            try:

                for member in data["query"]["categorymembers"]:
                    title = member["title"]
                    RESTART_KEY = member["sortkey"]
                    if _skip_word(title, True):
                        continue
                    print(title, RESTART_KEY)
                    word_data = _scrape_word(title)
                    word_writer.write(word_data)
                word_f.flush()
                # "cmstarthexsortkey" reset so as to avoid competition
                # with "continue_code".
                if 'continue' not in data:
                    break
                continue_code = data["continue"]["cmcontinue"]

                requests_params.update(
                    {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                )
            except Exception as e:
                print(RESTART_KEY)
                if isinstance(e, (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            )):
                    print("timed out")
                    requests_params.update({"cmstarthexsortkey": RESTART_KEY})
                    # 5 minute timeout. Immediately restarting after the
                    # connection has dropped appears to have led to
                    # 'Connection reset by peer' errors.
                    time.sleep(300)
                else:
                    raise


if __name__ == '__main__':

    RESTART_KEY = None
    os.makedirs('rich_lexicons', exist_ok=True)
    #_scrape_word('上')
    scrape()