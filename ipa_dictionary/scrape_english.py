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

languages = ['English']

working_directory = r'D:\Data\speech\dictionaries\rich_lexicons\english'
os.makedirs(working_directory, exist_ok=True)
lexicon_path = os.path.join(working_directory, 'english.jsonl')
morph_path = os.path.join(working_directory, 'english_morphs.jsonl')

_CATEGORY_TEMPLATE = "Category:{language} suffixes"
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

pos_sections = {'Verb', 'Adjective', 'Proper noun', 'Adnominal', 'Preposition',
                'Noun', 'Pronoun', 'Adverb','Interjection', 'Particle', 'Numeral', 'Counter', 'Conjunction',
                'Determiner', 'Postposition', "Letter"}
morphological_sections = {'Suffix', 'Prefix','Clitic'}
def _scrape_word(word:str):
    session = requests_html.HTMLSession()
    request = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    parsing = False
    section = ''
    word_data = []
    morphological_data = []
    alternative_spellings = []
    morphological_string = ''
    lettered = False
    for element in request.html.find('div.mw-parser-output', first=True).element.getchildren():
        if element.tag == 'h2':
            if element.find('span').text == 'English':
                parsing = True
            else:
                parsing = False
        if not parsing:
            continue

        if element.tag in {'h3', 'h4', 'h5', 'h6'}:
            section = element.find('span').text_content()
            if section == 'Alternative forms':
                continue
            if 'Etymology' in section:
                continue
            if section in {'Conjugation', 'Inflection', 'Usage notes'}:
                continue
            if section in pos_sections:
                word_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'sub_pos_tags': set(),
                    'written_forms': {word},
                    'definitions': set(),
                    'morphological_string': morphological_string,
                })
                word_data[-1]['pos_tags'].add(section)
                to_update = word_data[-1]
                if section == 'Letter':
                    lettered = True
            if section in morphological_sections:
                morphological_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'sub_pos_tags': set(),
                    'written_forms': {word} | set(alternative_spellings),
                    'definitions': set(),
                    'morphological_string': morphological_string,
                })
                morphological_data[-1]['pos_tags'].add(section)
                to_update = morphological_data[-1]

            continue
        if section == 'Alternative forms':
            alternative_spellings = []
            for x in element.text_content().split('\n'):
                if any(y in x for y in ['(archaic)', '(obsolete)']):
                    continue
                x = re.sub(r' \(.*\)', '', x)
                alternative_spellings.append(x)
        if section == 'Etymology':
            if '+' in element.text_content():
                morphological_string = element.text_content().replace('\u200e', '').strip()
                if morphological_string.startswith('From '):
                    morphological_string = ''
            continue
        if section in pos_sections | morphological_sections and element.tag == 'p':
            to_update['written_forms'].update(alternative_spellings)
            if '(clitic)' in element.text_content():
                to_update['sub_pos_tags'].add('clitic')
            if section == 'Verb':
                to_update['inflections'] = {}
                sg = element.xpath('b[contains(@class, "3|s|pres-form-of")]')
                if sg:
                    to_update['inflections']['3|s|pres'] = sg[0].text_content()
                pt = element.xpath('b[contains(@class, "pres|ptcp-form-of")]')
                if pt:
                    to_update['inflections']['gerund'] = pt[0].text_content()
                    to_update['inflections']['present_participle'] = pt[0].text_content()
                past = element.xpath('b[contains(@class, "past|and|past|ptcp-form-of")]')
                if past:
                    past = past[0].text_content()
                    to_update['inflections']['past'] = past
                    to_update['inflections']['past_participle'] = past
                else:
                    past = element.xpath('b[contains(@class, "past-form-of")]')
                    if past:
                        to_update['inflections']['past'] = past[0].text_content()
                    past = element.xpath('b[contains(@class, "past|ptcp-form-of")]')
                    if past:
                        to_update['inflections']['past_participle'] = past[0].text_content()
            elif section == 'Noun':
                to_update['inflections'] = {}
                plural = element.xpath('b[contains(@class, "p-form-of")]')
                if plural:
                    to_update['inflections']['plural'] = plural[0].text_content()
                for t in ['countable', 'uncountable']:
                    if t in element.text_content():
                        to_update['sub_pos_tags'].add(t)
            elif section in {'Adjective', 'Adverb'}:
                to_update['inflections'] = {}
                comparative = element.xpath('b[contains(@class, "comparative-form-of")]')
                if comparative:
                    comparative = comparative[0].text_content()
                    if 'more' not in comparative:
                        to_update['inflections']['comparative'] = comparative
                superlative = element.xpath('b[contains(@class, "superlative-form-of")]')
                if superlative:
                    superlative = superlative[0].text_content()
                    if 'most' not in superlative:
                        to_update['inflections']['superlative'] = superlative
            continue
        if section in pos_sections | morphological_sections and element.tag == 'ol':
            to_update['definitions'].update([x.text_content().split('\n')[0] for x in element.findall('li') if x.text_content().split('\n')[0]])
            continue
    filtered_word_data = []
    for w in word_data:
        if lettered and 'Letter' not in w['pos_tags']:
            continue
        for d in w['definitions']:
            if 'past participle' in d.lower():
                break
            if 'present participle' in d.lower():
                break
            if 'alternative form of' in d.lower():
                break
            if 'alternative spelling of' in d.lower():
                break
            if 'misspelling of' in d.lower():
                break
            if 'censored spelling of' in d.lower():
                break
            if 'pronunciation spelling of' in d.lower():
                break
            if 'initialism of' in d.lower():
                break
            if 'abbreviation of' in d.lower():
                break
            if '(initialism)' in d.lower():
                break
        else:
            filtered_word_data.append(w)

    collapsed_word_data = {}
    for x in filtered_word_data:
        if not x['pos_tags'] or not x['definitions']:
            continue
        pos = tuple(sorted(x['pos_tags']))
        key = (x['word'], pos)
        d = {k: v for k,v in x.items() if v and k not in ['word', 'pos_tags', 'pronunciations']}
        if key not in collapsed_word_data:
            collapsed_word_data[key] = d
        else:
            collapsed_word_data[key]['written_forms'].update(d['written_forms'])
            collapsed_word_data[key]['definitions'].update(d['definitions'])
    word_data = [{'key': k, **v} for k,v in collapsed_word_data.items()]
    return word_data, morphological_data

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
    with open(lexicon_path, 'a', encoding='utf8') as word_f, \
        open(morph_path, 'a', encoding='utf8') as morph_f:
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
                    if word_data:
                        word_writer.write_all(word_data)
                    if morpho_data:
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


if __name__ == '__main__':

    RESTART_KEY = None
    _scrape_word('neighbour')
    #scrape()