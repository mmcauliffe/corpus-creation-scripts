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
    urdu_word = None
    for w in words:
        if w.text.strip() != word:
            continue
        urdu_words = w.element.getparent().xpath('//b[@lang="ur"]')
        if not urdu_words:
            continue
        urdu_word = urdu_words[0].text_content()
    return urdu_word


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
    with open('rich_lexicons/japanese.jsonl', 'a', encoding='utf8') as word_f, \
        open('rich_lexicons/japanese_morphs.jsonl', 'a', encoding='utf8') as morph_f:
        word_writer = jsonlines.Writer(word_f, dumps=functools.partial(json.dumps, default=set_default, ensure_ascii=False))
        morph_writer = jsonlines.Writer(morph_f, dumps=functools.partial(json.dumps, default=set_default, ensure_ascii=False))
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
                    word_data, morpho_data = _scrape_word(title)
                    word_writer.write_all(word_data)
                    morph_writer.write_all(morpho_data)
                word_f.flush()
                morph_f.flush()
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

hindi_dictionary_path = r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\hindi_mfa.dict"
urdu_dictionary_path = r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\urdu_auto_mfa.dict"
hindi_to_urdu_path = r"C:\Users\michael\Documents\Dev\mfa-models\dictionary\training\hindi_to_urdu.dict"

if __name__ == '__main__':

    RESTART_KEY = None
    with open(hindi_dictionary_path, 'r', encoding='utf8') as inf, open(urdu_dictionary_path, 'w', encoding='utf8') as outf, open(hindi_to_urdu_path, 'w', encoding='utf8') as outf2:
        for line in inf:
            line = line.strip()
            if not line:
                continue
            word, pron = line.split(maxsplit=1)
            print(word)

            urdu_word = _scrape_word(word)
            if urdu_word is None:
                continue
            print(word, urdu_word, pron)
            outf.write(f"{urdu_word}\t{pron}\n")
            outf2.write(f"{urdu_word}\t{' '.join(word)}\n")