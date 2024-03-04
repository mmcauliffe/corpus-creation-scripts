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

config = wikipron.Config(key="swe", dialect='Sweden')
print(config.language)
print(config.dialect)

with open('swedish.tsv', 'w', encoding='utf8') as f:
    for word, pron in wikipron.scrape(config):
        print(word, pron)
        f.write(f"{word}\t{pron}\n")
