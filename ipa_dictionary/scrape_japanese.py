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
    parsing = False
    section = ''
    word_data = []
    morphological_data = []
    alternative_spellings = []
    pronunciations = []
    for element in request.html.find('div.mw-parser-output', first=True).element.getchildren():
        if element.tag == 'h2':
            if element.find('span').text == 'Japanese':
                parsing = True
            else:
                parsing = False
        if not parsing:
            continue

        if element.tag in {'h3', 'h4', 'h5', 'h6'}:
            section = element.find('span').text_content()
            if 'Etymology' in section:
                alternative_spellings = []
                pronunciations = []
                continue
            if section in {'Conjugation', 'Inflection', 'Usage notes'}:
                continue
            if section in pos_sections:
                word_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'written_forms': {word},
                    'definitions': set(),
                })
                word_data[-1]['pos_tags'].add(section)
                to_update = word_data[-1]
            if section in morphological_sections:
                morphological_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'written_forms': {word} | set(alternative_spellings),
                    'definitions': set(),
                })
                morphological_data[-1]['pos_tags'].add(section)
                to_update = morphological_data[-1]

            continue
        if section in {'Phrase', 'Idiom'}:
            return [], []
        if section and element.tag == 'table' and 'class' in element.attrib and  'floatright' in element.attrib['class']:
            head = element.xpath('tbody//th')[0]
            if 'Alternative spelling' in head:
                continue
            rows = element.xpath('tbody//td/span[@class = "Jpan"]')
            alternative_spellings = [x.text_content() for x in rows]

        if section == 'Pronunciation':
            if not pronunciations:
                pronunciations = element.xpath('ul//span[@class = "IPA"]')
                if not pronunciations:
                    pronunciations = element.xpath('li//span[@class = "IPA"]')
                if not pronunciations:
                    continue
                pronunciations = [process_pronunciation(x.text_content()) for x in pronunciations if '/' not in x]
            continue
        if section in pos_sections | morphological_sections and element.tag == 'p':
            span = element.find('span')
            if span is None:
                continue
            if 'id' not in span.attrib:
                continue
            to_update['written_forms'].update(alternative_spellings)
            if pronunciations:
                to_update['pronunciations'] = set(pronunciations)
            to_update['written_forms'].add(span.attrib['id'])
            to_update['written_forms'].update([x.text_content() for x in element.xpath('strong') if '(' not in x.text_content()])
            sub_pos_tags = element.find('i')
            if sub_pos_tags is not None:
                to_update['pos_tags'].update(sub_pos_tags.text_content().strip().split())
                to_update['pos_tags'] -= {'or'}
            continue
        if section in pos_sections | morphological_sections and element.tag == 'ol':
            to_update['definitions'].update([x.text_content().split('\n')[0] for x in element.findall('li')])
            to_update['inflections'] = {}
            continue
        if section in {'Conjugation', 'Inflection'} and element.tag == 'div' and element.attrib['class'] == 'NavFrame':
            if any(x in element.find('div').text_content() for x in {'する', 'Classical'}):
                continue
            rows = element.xpath('div[@class = "NavContent"]//tr')
            for r in rows:
                head = r.find('th')
                if head is None or 'colspan' in head.attrib:
                    continue
                cells = r.xpath('td/span')
                if not cells:
                    continue
                conjugation = head.text_content().strip()
                written_forms = []
                for s in cells:
                    html_string = lxml.etree.tostring(s,encoding='utf8').decode('utf8').strip()
                    html_string = re.sub(r'<br/?>', '\n',html_string)
                    html_string = re.sub(r'</?span.*?>', '', html_string)
                    html_string = re.sub(r'[¹²³⁴⁵]', '', html_string)
                    written_forms.extend([x for x in html_string.split() if not re.match(r'^[a-zA-Z0-9 ]+$', x)])
                to_update['inflections'][conjugation] = {'word': written_forms[0], 'written_forms': written_forms}
    collapsed_word_data = {}
    for x in word_data:
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
    word_data = [{'key': k, **v} for k,v in  collapsed_word_data.items()]
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


if __name__ == '__main__':

    RESTART_KEY = None
    os.makedirs('rich_lexicons', exist_ok=True)
    #_scrape_word('隠密')
    scrape()