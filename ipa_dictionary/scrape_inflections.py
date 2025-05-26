
import requests
import time
import re
import requests_html

HTTP_HEADERS = {
    "User-Agent": (
        f"Montreal-Forced-Aligner/3.1.0"
        "(https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) "
        f"requests/{requests.__version__}"
    ),
}
_PAGE_TEMPLATE = "https://en.wiktionary.org/wiki/{word}"

LANGUAGE = 'Serbo-Croatian'

CODES = {
    'Czech': 'cs',
    'Spanish': 'es',
    'Serbo-Croatian': 'sh',
}

LANGUAGE_CODE = CODES[LANGUAGE]
word_path = r"C:\Users\micha\Documents\Dev\mfa-models\dictionary\training\spanish_latin_america_mfa.dict"

FOUND_WORDS = set()


def load_words():
    word_set = set()
    with open(word_path, 'r', encoding='utf8') as f:
        for line in f:
            word, _ = line.split(maxsplit=1)
            word_set.add(word)
    return word


def parse_word(word_string):
    if word_string.startswith('-') or word_string.endswith('-'):
        return []
    if re.search(r"[\d.,]", word_string):
        return []
    words = re.split(r'[-\s]', word_string)
    return words


def scrape(lemmas=False):
    word_set = load_words()
    global RESTART_KEY
    if lemmas:
        category = f'Category:{LANGUAGE} lemmas'
    else:
        category = f'Category:{LANGUAGE} non-lemma forms'
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "500",
        "cmprop": "ids|title|timestamp|sortkey",
    }
    current = 0
    with open(f'rich_lexicons/{LANGUAGE.lower()}_forms.txt', 'a', encoding='utf8') as out_f:
        while True:
            data = requests.get(
                "https://en.wiktionary.org/w/api.php?",
                params=requests_params,
                headers=HTTP_HEADERS,
            ).json()
            try:
                for member in data["query"]["categorymembers"]:
                    title = member["title"]
                    RESTART_KEY = member["sortkey"]
                    #print(title)
                    words = parse_word(title)
                    for w in words:
                        if w not in word_set and w not in FOUND_WORDS:
                            FOUND_WORDS.add(w)
                            out_f.write(f"{w}\n")
                            out_f.flush()
                # "cmstarthexsortkey" reset so as to avoid competition
                # with "continue_code".
                if 'continue' not in data:
                    break
                continue_code = data["continue"]["cmcontinue"]

                requests_params.update(
                    {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                )
                current += len(data["query"]["categorymembers"])
                print(f"Processed {current} entries")
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


def _scrape_conjugations(word:str):
    session = requests_html.HTMLSession()
    response = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    elements = response.html.xpath(f'//td/span[contains(@class, "Latn") and @lang="{LANGUAGE_CODE}"]//a[contains(@class, "new")]')

    words = set()
    for x in elements:
        words.update(x.text.split())
    return words


def _scrape_declension(word:str):
    session = requests_html.HTMLSession()
    response = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    elements = response.html.xpath(f'//table[contains(@class, "inflection-table")]//td/span[@lang="{LANGUAGE_CODE}"]')

    words = set()
    for x in elements:
        words.update(x.text.split())
    return words


def _scrape_derived(word:str):
    session = requests_html.HTMLSession()
    response = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    elements = response.html.xpath(f'//table[contains(@class, "inflection-table")]//td/span[@lang="{LANGUAGE_CODE}"]')

    words = set()
    for x in elements:
        words.update(x.text.split())
    return words


def _scrape_related(word:str):
    session = requests_html.HTMLSession()
    response = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    elements = response.html.xpath(f'//div[h4[text()="Related terms"]]/following-sibling::div//span[@lang="{LANGUAGE_CODE}" and a[contains(@class, "new")]]')
    words = set()
    for x in elements:
        words.update(x.text.split())
    return words


def scrape_verb_conjugations():
    word_set = load_words()
    global RESTART_KEY
    category = f'Category:{LANGUAGE} verbs'
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "500",
        "cmprop": "ids|title|timestamp|sortkey",
    }
    current = 0
    with open(f'rich_lexicons/{LANGUAGE.lower()}_forms.txt', 'a', encoding='utf8') as out_f:
        while True:
            data = requests.get(
                "https://en.wiktionary.org/w/api.php?",
                params=requests_params,
                headers=HTTP_HEADERS,
            ).json()
            try:
                for member in data["query"]["categorymembers"]:
                    title = member["title"]
                    RESTART_KEY = member["sortkey"]
                    print(title)
                    words = _scrape_conjugations(title)
                    for w in words:
                        if w not in word_set and w not in FOUND_WORDS:
                            FOUND_WORDS.add(w)
                            out_f.write(f"{w}\n")
                            out_f.flush()
                # "cmstarthexsortkey" reset so as to avoid competition
                # with "continue_code".
                if 'continue' not in data:
                    break
                continue_code = data["continue"]["cmcontinue"]

                requests_params.update(
                    {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                )
                current += len(data["query"]["categorymembers"])
                print(f"Processed {current} entries")
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


def scrape_declensions():
    word_set = load_words()
    global RESTART_KEY
    categories = [
        f'Category:{LANGUAGE} adjectives',
        f'Category:{LANGUAGE} nouns',
        f'Category:{LANGUAGE} proper nouns',
        f'Category:{LANGUAGE} pronouns',
        f'Category:{LANGUAGE} determiners',
        f'Category:{LANGUAGE} numerals',
    ]
    current = 0
    with open(f'rich_lexicons/{LANGUAGE.lower()}_forms.txt', 'a', encoding='utf8') as out_f:
        for category in categories:
            requests_params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "500",
                "cmprop": "ids|title|timestamp|sortkey",
            }
            while True:
                data = requests.get(
                    "https://en.wiktionary.org/w/api.php?",
                    params=requests_params,
                    headers=HTTP_HEADERS,
                ).json()
                try:
                    for member in data["query"]["categorymembers"]:
                        title = member["title"]
                        RESTART_KEY = member["sortkey"]
                        print(title)
                        words = _scrape_declension(title)
                        for w in words:
                            if w not in word_set and w not in FOUND_WORDS:
                                FOUND_WORDS.add(w)
                                out_f.write(f"{w}\n")
                                out_f.flush()
                    # "cmstarthexsortkey" reset so as to avoid competition
                    # with "continue_code".
                    if 'continue' not in data:
                        break
                    continue_code = data["continue"]["cmcontinue"]

                    requests_params.update(
                        {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                    )
                    current += len(data["query"]["categorymembers"])
                    print(f"Processed {current} entries")
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


def scrape_related():
    word_set = load_words()
    global RESTART_KEY
    categories = [
        f'Category:{LANGUAGE} adjectives',
        f'Category:{LANGUAGE} nouns',
        f'Category:{LANGUAGE} proper nouns',
        f'Category:{LANGUAGE} pronouns',
        f'Category:{LANGUAGE} determiners',
        f'Category:{LANGUAGE} numerals',
        f'Category:{LANGUAGE} verbs',
    ]
    current = 0
    skip = True
    with open(f'rich_lexicons/{LANGUAGE.lower()}_forms.txt', 'a', encoding='utf8') as out_f:
        for category in categories:
            requests_params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "500",
                "cmprop": "ids|title|timestamp|sortkey",
            }
            while True:
                try:
                    d = requests.get(
                        "https://en.wiktionary.org/w/api.php?",
                        params=requests_params,
                        headers=HTTP_HEADERS,
                    )
                    data = d.json()
                except requests.exceptions.JSONDecodeError:
                    print(d)
                    raise
                try:
                    for member in data["query"]["categorymembers"]:
                        title = member["title"]
                        RESTART_KEY = member["sortkey"]
                        print(title)
                        if title == 'vrchovatý':
                            skip = False
                        if skip:
                            continue
                        words = _scrape_related(title)
                        for w in words:
                            if w not in word_set and w not in FOUND_WORDS:
                                FOUND_WORDS.add(w)
                                out_f.write(f"{w}\n")
                                out_f.flush()
                    # "cmstarthexsortkey" reset so as to avoid competition
                    # with "continue_code".
                    if 'continue' not in data:
                        break
                    continue_code = data["continue"]["cmcontinue"]

                    requests_params.update(
                        {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                    )
                    current += len(data["query"]["categorymembers"])
                    print(f"Processed {current} entries")
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


def scrape_suffixes():
    word_set = load_words()
    global RESTART_KEY
    categories = [
        f'Category:{LANGUAGE} suffixes',
    ]
    current = 0
    with open(f'rich_lexicons/{LANGUAGE.lower()}_suffixes.txt', 'a', encoding='utf8') as out_f:
        for category in categories:
            requests_params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "500",
                "cmprop": "ids|title|timestamp|sortkey",
            }
            while True:
                data = requests.get(
                    "https://en.wiktionary.org/w/api.php?",
                    params=requests_params,
                    headers=HTTP_HEADERS,
                ).json()
                try:
                    for member in data["query"]["categorymembers"]:
                        title = member["title"]
                        RESTART_KEY = member["sortkey"]
                        print(title)
                        words = _scrape_declension(title)
                        for w in words:
                            if w not in word_set and w not in FOUND_WORDS:
                                FOUND_WORDS.add(w)
                                out_f.write(f"{w}\n")
                                out_f.flush()
                    # "cmstarthexsortkey" reset so as to avoid competition
                    # with "continue_code".
                    if 'continue' not in data:
                        break
                    continue_code = data["continue"]["cmcontinue"]

                    requests_params.update(
                        {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                    )
                    current += len(data["query"]["categorymembers"])
                    print(f"Processed {current} entries")
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


def scrape_prefixes():
    global RESTART_KEY
    categories = [
        f'Category:{LANGUAGE} prefixes',
    ]
    current = 0
    with open(f'rich_lexicons/{LANGUAGE.lower()}_prefixes.txt', 'a', encoding='utf8') as out_f:
        for category in categories:
            requests_params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "500",
                "cmprop": "ids|title|timestamp|sortkey",
            }
            while True:
                data = requests.get(
                    "https://en.wiktionary.org/w/api.php?",
                    params=requests_params,
                    headers=HTTP_HEADERS,
                ).json()
                try:
                    for member in data["query"]["categorymembers"]:
                        title = member["title"]
                        RESTART_KEY = member["sortkey"]
                        print(title)
                        if not title.endswith('-'):
                            continue
                        out_f.write(f"{title}\n")
                        out_f.flush()
                    # "cmstarthexsortkey" reset so as to avoid competition
                    # with "continue_code".
                    if 'continue' not in data:
                        break
                    continue_code = data["continue"]["cmcontinue"]

                    requests_params.update(
                        {"cmcontinue": continue_code, "cmstarthexsortkey": None}
                    )
                    current += len(data["query"]["categorymembers"])
                    print(f"Processed {current} entries")
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
    #scrape(lemmas=True)
    #scrape(lemmas=False)
    scrape_verb_conjugations()
    scrape_declensions()
    #scrape_suffixes()
    #scrape_prefixes()
    scrape_related()
