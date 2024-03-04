import itertools
import os

import unicodedata
import re
import requests_html
import requests
import segments
import time
import jsonlines
import json
import functools

languages = ['Chinese']

working_directory = r'D:\Data\speech\dictionaries\rich_lexicons\chinese'
os.makedirs(working_directory, exist_ok=True)
lexicon_path = os.path.join(working_directory, 'chinese.jsonl')
morph_path = os.path.join(working_directory, 'chinese_morphs.jsonl')

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
    pron = pron.replace('/', '').strip()
    pron = unicodedata.normalize("NFD", pron)
    pron = segments.Tokenizer()(pron, ipa=True).replace(' #', '')
    for c in cleanup_characters:
        pron = pron.replace(c, '')
    return pron

IPA_XPATH_SELECTOR = '//span[@class = "IPA"]'
LANGUAGE_SELECTOR = '//h2[span = "{language}"]'

pos_sections = {'Verb', 'Adjective', 'Proper noun', 'Adnominal', 'Preposition',
                'Noun', 'Pronoun', 'Adverb','Interjection', 'Particle', 'Numeral', 'Counter', 'Conjunction',
                'Determiner', 'Postposition', "Letter", 'Classifier'}
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
    pronunciations = {}
    morphological_string = ''
    lettered = False
    for element in request.html.find('div.mw-parser-output', first=True).element.getchildren():
        if element.tag == 'h2':
            if element.find('span').text == 'Chinese':
                parsing = True
            else:
                parsing = False
        if not parsing:
            continue

        if element.tag in {'h3', 'h4', 'h5', 'h6'}:
            old_section = section
            section = element.find('span').text_content()
            if 'Etymology' in section:
                alternative_spellings = []
                pronunciations = {}
                continue
            if section == 'Alternative forms':
                elements = element.xpath('ul//span')
                alternative_spellings.extend([x.text_content() for x in elements])
            if section in {'Conjugation', 'Inflection', 'Usage notes'}:
                continue
            if section == 'Definitions':
                word_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'sub_pos_tags': set(),
                    'written_forms': {word},
                    'definitions': set(),
                })
                to_update = word_data[-1]

            if section in pos_sections:
                word_data.append({
                    'word': word,
                    'pos_tags': set(),
                    'sub_pos_tags': set(),
                    'written_forms': {word},
                    'definitions': set(),
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
                })
                morphological_data[-1]['pos_tags'].add(section)
                to_update = morphological_data[-1]

            continue
        if section in {'Phrase', 'Idiom'}:
            return [], []
        if element.tag == 'table' and section != 'Derived terms':
            header_cells = element.find('tbody').findall('tr')
            for row in header_cells:
                th = row.find('th')
                if th is None:
                    continue
                link = th.find('a')
                if link is None:
                    continue
                try:
                    if 'title' in link.attrib:
                        form = th.find('span')
                        if form is not None:
                            form = form.find('span')
                        if form is not None:
                            alternative_spellings.append(form[0].text_content().strip())
                except IndexError:
                    pass
        if (section in pos_sections | morphological_sections or section == 'Definitions') and element.tag == 'ol':
            to_update['definitions'].update([x.text_content().split('\n')[0] for x in element.findall('li') if x.text_content().split('\n')[0]])
            continue
        if 'Pronunciation' in section and element.tag == 'div':
            try:
                ipa_panel = element.find('div').xpath('div[@class= "vsHide"]')
                langs = ipa_panel[0].find('ul').findall('li')
            except (AttributeError, IndexError):
                return [], []
            for l in langs:
                lang = l.find('a').text_content()
                if lang not in pronunciations:
                    pronunciations[lang] = {}
                dialects = l.find('ul').findall('li')
                for d in dialects:
                    dialect = ', '.join([x.text_content().strip() for x in d.find('small').findall('i')])
                    if dialect not in pronunciations[lang]:
                        pronunciations[lang][dialect] = set()
                    for e in d.find('ul').findall('li'):
                        ipa = e.xpath('span[@class = "IPA"]')
                        if not ipa:
                            continue
                        prons = [process_pronunciation(x) for x in ipa[0].text_content().strip().split(',')]
                        pronunciations[lang][dialect].update(prons)
        if (section in pos_sections | morphological_sections or section == 'Definitions') and element.tag == 'p':
            if pronunciations:
                to_update['pronunciations'] = pronunciations
            to_update['written_forms'].update(alternative_spellings)

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
        d = {k: v for k,v in x.items() if v and k not in ['word', 'pos_tags']}
        if key not in collapsed_word_data:
            collapsed_word_data[key] = d
        else:
            collapsed_word_data[key]['written_forms'].update(d['written_forms'])
            collapsed_word_data[key]['definitions'].update(d['definitions'])
            if 'pronunciations' in d:
                collapsed_word_data[key]['pronunciations'] = d['pronunciations']
    word_data = [{'key': k, **v} for k,v in collapsed_word_data.items()]

    collapsed_morpho_data = {}
    for x in morphological_data:
        if not x['pos_tags'] or not x['definitions']:
            continue
        pos = tuple(sorted(x['pos_tags']))
        key = (x['word'], pos)
        d = {k: v for k,v in x.items() if v and k not in ['word', 'pos_tags']}
        if key not in collapsed_morpho_data:
            collapsed_morpho_data[key] = d
        else:
            collapsed_morpho_data[key]['written_forms'].update(d['written_forms'])
            collapsed_morpho_data[key]['definitions'].update(d['definitions'])
            if 'pronunciations' in d:
                collapsed_morpho_data[key]['pronunciations'] = d['pronunciations']
    morphological_data = [{'key': k, **v} for k,v in collapsed_morpho_data.items()]
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

    RESTART_KEY = '430a43'
    _scrape_word('二')
    #scrape()