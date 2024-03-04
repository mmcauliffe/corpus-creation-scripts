import wikipron
import unicodedata
import re
import requests_html
import pkg_resources
import requests
import logging
import segments
import time
import functools
standard_output_file = r'mandarin_hani_standard.tsv'
beijing_output_file = r'mandarin_hani_beijing.tsv'
taiwan_output_file = r'mandarin_hani_taiwan.tsv'



config = wikipron.Config(key="cmn", dialect="Standard Chinese")
print(config.language)
print(config.dialect)


# Select pron from within this li
_PRON_XPATH_TEMPLATE = """
    //div[@class="vsHide"]
        //ul
            //li[(a[@title="w:Mandarin Chinese"])]
"""
DIALECT_XPATH_SELECTOR = """
    //ul
        //li"""

IPA_XPATH_SELECTOR = '//span[@class = "IPA"]'
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


def _skip_date(date_from_word: str, cut_off_date: str) -> bool:
    return date_from_word > cut_off_date

_PAGE_TEMPLATE = "https://en.wiktionary.org/wiki/{word}"
# Http headers for api call
HTTP_HEADERS = {
    "User-Agent": (
        f"WikiPron/{pkg_resources.get_distribution('wikipron').version} "
        "(https://github.com/kylebgorman/wikipron) "
        f"requests/{requests.__version__}"
    ),
}
_PHONEMES_REGEX = r"/(.+?)/"
_PHONES_REGEX = r"\[(.+?)\]"

_TONES_REGEX = r"[˥˦˧˨˩⁰¹²³⁴⁵⁶⁷⁸⁹⁻◌̋ ◌̌ ◌̏ ◌̀ ◌́ ◌̂ ◌̄ ◌᷄◌᷅◌᷆◌᷇◌᷈◌᷉↑↓↗↘]"
_PARENS_REGEX = rf"⁽{_TONES_REGEX}+⁾"


def _skip_pron(pron: str, skip_spaces: bool) -> bool:
    if "-" in pron:
        return True
    if skip_spaces and (" " in pron or "\u00A0" in pron):
        return True
    return False

def _scrape_once(data):
    session = requests_html.HTMLSession()
    for member in data['query']["search"]:
        title = member["title"]
        if _skip_word(title, True):
            continue
        request = session.get(
            _PAGE_TEMPLATE.format(word=title), timeout=10, headers=HTTP_HEADERS
        )
        mapping = extract_word_pron_cmn(title, request)
        for dialect, pron in mapping.items():
            # Pronunciation processing is done in NFD-space;
            # we convert back to NFC afterwards.
            mapping[dialect] = unicodedata.normalize("NFC", pron)
            # 'cast' is required 'normalize' doesn't return a 'Pron'
        yield title, mapping


def _get_process_pron(
    stress: bool,
    syllable_boundaries: bool,
    segment: bool,
    tone: bool,
):
    processors = []
    if not stress:
        processors.append(functools.partial(re.sub, r"[ˈˌ]", ""))
    if not syllable_boundaries:
        processors.append(functools.partial(re.sub, r"\.", ""))
    if not tone:
        processors.append(functools.partial(re.sub, _PARENS_REGEX, ""))
        processors.append(functools.partial(re.sub, _TONES_REGEX, ""))
    if segment:
        processors.append(
            functools.partial(segments.Tokenizer(), ipa=True)
        )
    prosodic_markers = frozenset(["ˈ", "ˌ", "."])

    def wrapper(pron):
        for processor in processors:
            pron = processor(pron)
        # GH-59: Skip prons that are empty, or have only stress marks or
        # syllable boundaries.
        if any(ch not in prosodic_markers for ch in pron):
            return pron

    return wrapper


process_pron = _get_process_pron(
            True, True, True, True
        )

def yield_pron(
    request_html,
    ipa_xpath_selector,
):
    for ipa_element in request_html.xpath(ipa_xpath_selector):
        m = re.search(config.ipa_regex, ipa_element.text)
        #print(m, ipa_element)
        if not m:
            continue
        pron = m.group(1)
        # Removes parens around various segments.
        pron = pron.replace("(", "").replace(")", "")
        if _skip_pron(pron, False):
            continue
        try:
            # All pronunciation processing is done in NFD-space.
            pron = unicodedata.normalize("NFD", pron)
            pron = process_pron(pron)
        except IndexError:
            logging.info(
                "IndexError encountered processing %s during scrape of %s",
                pron,
                config.language,
            )
            continue
        if pron:
            # The segments package inserts a # in-between spaces.
            if not config.skip_spaces_pron:
                pron = pron.replace(" #", "")
            yield pron


def yield_cmn_pron(
    request
):
    dialect_mapping = {}
    for li_container in request.html.xpath(_PRON_XPATH_TEMPLATE):
        dialects = li_container.xpath(DIALECT_XPATH_SELECTOR)
        for dialect in dialects:
            #print("DIALECT", dialect.html)
            d = dialect.xpath('//i[(a[@title="w:Standard Chinese"])]', first=True)
            #print("D", d)
            if d is None:
                continue
            #print("DHTML", d.html)
            try:
                pronunciation = list(yield_pron(dialect, IPA_XPATH_SELECTOR))[0]
            except IndexError:
                continue
            dialect_listing = [x.text for x in dialect.find('i', first=True).find('a')]
            #print(dialect_listing, pronunciation)
            if 'erhua' in dialect_listing:
                dialect = 'Beijing'
            elif 'Taiwan' in dialect_listing:
                dialect = 'Taiwan'
            elif 'Mainland' in dialect_listing or any('Standard Chinese' in x for x in dialect_listing):
                dialect = 'Standard Chinese'
            else:
                continue
            if dialect not in dialect_mapping:
                dialect_mapping[dialect] = pronunciation
    return dialect_mapping
    #yield from yield_pron(li_container, IPA_XPATH_SELECTOR, config)

def extract_word_pron_cmn(
    word, request
):
    prons = yield_cmn_pron(request)
    return prons

categories = [
    'incategory:"Beginning Mandarin"',
    'incategory:"Elementary Mandarin"',
    'incategory:"Intermediate Mandarin"',
    'incategory:"Advanced Mandarin"',
    'incategory:"Mandarin adverbs"',
    'incategory:"Mandarin determiners"',
    'incategory:"Mandarin interjections"',
    'incategory:"Mandarin numerals"',
    'incategory:"Mandarin conjunctions"',
    'incategory:"Mandarin classifiers"',
    'incategory:"Mandarin circumpositions"',
    'incategory:"Mandarin particles"',
    'incategory:"Mandarin postpositions"',
    'incategory:"Mandarin prepositions"',
    'incategory:"Mandarin pronouns"',
    'incategory:"Mandarin proper nouns"',
    'incategory:"Hakka verbs"',
    'incategory:"Mandarin verbs"',
    'incategory:"Hokkien Chinese"',
    'incategory:"Hakka nouns"',
    'incategory:"Teochew nouns"',
    'incategory:"Xiang nouns"',
    'incategory:"Gan nouns"',
    'incategory:"Wu nouns"',
    'incategory:"Jin nouns"',
    'incategory:"Min Bei nouns"',
    'incategory:"Min Dong nouns"',
    'incategory:"Taishanese nouns"',
    'incategory:"Hokkien nouns"',
    'incategory:"Japanese nouns"',
    'incategory:"Min Nan nouns"',
    'incategory:"Mandarin nouns"',
    'incategory:"Mandarin words containing toneless variants"',
]
categories = ['incategory:"Mandarin words containing toneless variants"']

defaults_search_string ='incategory:"Chinese terms with IPA pronunciation" -incategory:"Chinese obsolete terms" -incategory:"Min Nan Pe̍h-ōe-jī forms" -incategory:"Chinese variant forms" -incategory:"Mandarin pinyin" -incategory:"Translingual letters" -incategory:"English terms with IPA pronunciation" -incategory:"Chinese simplified forms" -incategory:"Chinese terms written in foreign scripts" -incategory:"Chinese derogatory terms"'

def construct_search_string(category):
    search_string_list = [defaults_search_string]
    for c in categories:
        if c == category:
            break
        search_string_list.append('-'+c)
    search_string_list.append(category)
    return ' '.join(search_string_list)

def scrape(search_string):
    """Scrapes with a given configuration."""
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_string,
        "srlimit": "500",
        "srsort": "create_timestamp_asc",
        'sroffset': "0",
        "srprop": "titlesnippet|timestamp",
    }
    while True:
        t = requests.get(
            "https://en.wiktionary.org/w/api.php?",
            params=requests_params,
            headers=HTTP_HEADERS,
        )
        print(t.url)
        data = requests.get(
            "https://en.wiktionary.org/w/api.php?",
            params=requests_params,
            headers=HTTP_HEADERS,
        ).json()
        print(data)
        print(f"Processing {requests_params['sroffset']} of {data['query']['searchinfo']['totalhits']}")
        try:
            for member in data['query']["search"]:
                yield member["title"]

            if 'continue' not in data:
                break
            requests_params.update(
                {"sroffset": data['continue']['sroffset']}
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):
            print("timed out")
            # 5 minute timeout. Immediately restarting after the
            # connection has dropped appears to have led to
            # 'Connection reset by peer' errors.
            time.sleep(300)


languages = ['Chinese', 'Japanese', 'Bulgarian', 'Serbo-Croatian', 'Czech', 'French', 'German', 'Hausa', 'Korean', 'Polish',
             'Portuguese', 'Russian', 'Spanish', 'Tamil', 'Turkish', 'Ukrainian', 'Vietnamese', 'English']
for lang in languages:
    output_file = f'derogatory/{lang.lower()}.txt'
    search_strings = [
        #f'incategory:"{lang} derogatory terms"',
        f'incategory:"{lang} offensive terms"',
        f'incategory:"{lang} religious slurs"']
    with open(output_file, 'w', encoding='utf8') as f:
        for search_string in search_strings:
            for word in scrape(' '.join([f'incategory:"{lang} terms with IPA pronunciation"' ,search_string])):
                f.write(f"{word}\n")