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

config = wikipron.Config(key="bul")
print(config.language)
print(config.dialect)

with open('bulgarian.tsv', 'w', encoding='utf8') as f:
    for word, pron in wikipron.scrape(config):
        f.write(f"{word}\t{pron}\n")