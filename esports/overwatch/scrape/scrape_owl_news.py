import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json
import selenium
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
opts = Options()
opts.headless = True

base_dir = r'D:\Data\speech\esports\overwatch_texts'
output_path = os.path.join(base_dir, 'links.txt')

if not os.path.exists(output_path):
    URL = 'https://overwatchleague.com/en-us/news/'

    links_to_scrape = set()
    last_count = 0
    with Firefox(options=opts) as browser:
        browser.get(URL)
        print(browser.title)
        print(browser)
        while True:
            load_more_reached = False
            if len(browser.find_elements_by_css_selector('div')) == last_count:
                break
            last_count = browser.find_elements_by_css_selector('div')
            for d in browser.find_elements_by_css_selector('div'):
                try:
                    print(d.text)
                except selenium.common.exceptions.StaleElementReferenceException:
                    continue
                links = d.find_elements_by_css_selector('a')
                if not links:
                    continue

                for link in links:
                    print(link.text)
                    href = link.get_property('href')
                    print(href)
                    if href.startswith(URL):
                        if href not in links_to_scrape:
                            with open(output_path, 'a') as f:
                                f.write(href+'\n')
                        links_to_scrape.add(href)
                    if link.text.lower() == 'load more':
                        link.click()
                        load_more_reached = True
                        break
                if load_more_reached:
                    break
    print(links_to_scrape)
    error
else:
    links_to_scrape = []
    with open(output_path, 'r') as f:
        for line in f:
            links_to_scrape.append(line.strip())

for link in links_to_scrape:
    name = link.split('/')[-1]
    link_out = os.path.join(base_dir, name.replace('-', '_') + '.txt')
    if os.path.exists(link_out):
        continue
    with Firefox(options=opts) as browser:
        print(name)
        browser.get(link)
        time.sleep(10)
        texts = browser.find_elements_by_css_selector('p')
        print(len(texts))
        actual_texts = []
        for text in texts:
            time.sleep(1)
            if text.get_attribute('class'):
                continue
            actual_texts.append(text.text)
        if actual_texts:
            actual_texts = actual_texts[1:]
        with open(link_out, 'w', encoding='utf8') as f:
            for line in actual_texts:
                f.write(line + '\n')

expectedText = 'CardsContainer'
card_container = browser.find_element(by=By.XPATH, value="//div[contains(text(),'"+expectedText+"')]")
print(card_container)

print(browser.find_elements(title='Load More'))

browser.close()

error

URL = 'https://dotesports.com/overwatch/page/2'
response = requests.get(URL)
#print(response.text)

soup = BeautifulSoup(response.content, 'html.parser')
posts = soup.find_all(class_='post')
print(len(posts))
for p in posts:
    post_url = p.find('a').get('href')

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
print(match.groups()[0])
t = json.loads(match.groups()[0])
print(t.keys())
print(t['props']['pageProps'].keys())
for b in t['props']['pageProps']['blocks']:
    print(b)