
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


def load_words():
    word_set = set()
    word_path = r"C:\Users\micha\Documents\Dev\mfa-models\dictionary\training\spanish_spain_mfa.dict"
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

def scrape():
    word_set = load_words()
    global RESTART_KEY
    category = 'Category:Spanish lemmas'
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "500",
        "cmprop": "ids|title|timestamp|sortkey",
    }
    current = 0
    found_set = set()
    with open('rich_lexicons/spanish_forms.txt', 'a', encoding='utf8') as word_f:
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
                        if w not in word_set and w not in found_set:
                            found_set.add(w)
                            word_f.write(f"{w}\n")
                            word_f.flush()
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

def _scrape_word(word:str):
    session = requests_html.HTMLSession()
    response = session.get(
        _PAGE_TEMPLATE.format(word=word), timeout=10, headers=HTTP_HEADERS
    )
    elements = response.html.xpath(f'//span[contains(@class, "lang-es") and contains(@class, "verb-form-{word}-form-of")]//a[contains(@class, "new")]')

    words = [x.text for x in elements]
    return words

def scrape_combined_forms():
    word_set = load_words()
    global RESTART_KEY
    category = 'Category:Spanish verbs'
    requests_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "500",
        "cmprop": "ids|title|timestamp|sortkey",
    }
    current = 0
    found_set = set()
    with open('rich_lexicons/spanish_forms.txt', 'a', encoding='utf8') as word_f:
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
                    words = _scrape_word(title)
                    for w in words:
                        if w not in word_set and w not in found_set:
                            found_set.add(w)
                            word_f.write(f"{w}\n")
                            word_f.flush()
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
    scrape_combined_forms()