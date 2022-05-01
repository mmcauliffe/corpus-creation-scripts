import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json

base_dir = r'D:\Data\speech\esports\overwatch_texts'
output_path = os.path.join(base_dir, 'dot_links.txt')

base_url = 'https://dotesports.com/overwatch/page/{}'

index = 1

if not os.path.exists(output_path):
    links_to_scrape = set()
    while True:
        print(index)
        URL = base_url.format(index)
        response = requests.get(URL)
        if response.status_code == 404:
            break
        #print(response.text)

        soup = BeautifulSoup(response.content, 'html.parser')
        posts = soup.find_all('h3', attrs={'class':'entry-title'})
        print(len(posts))
        for p in posts:
            href = p.find('a')['href']
            links_to_scrape.add(href)
        index += 1

    print(links_to_scrape)

    with open(output_path, 'w') as f:
        for link in sorted(links_to_scrape):
            if not isinstance(link, str):
                continue
            f.write(link + '\n')
else:

    links_to_scrape = []
    with open(output_path, 'r') as f:
        for line in f:
            links_to_scrape.append(line.strip())


for link in links_to_scrape:
    print(link)
    name = link.split('/')[-1]
    link_out = os.path.join(base_dir, name.replace('-', '_') + '.txt')
    if os.path.exists(link_out):
        continue
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    body = soup.find('div', attrs={'class': 'col-lg-7'})
    if body is None:
        body = soup.find('div', attrs={'class': 'col-lg-8'})
    if body is None:
        body = soup.find('div', attrs={'class': 'entry-content'})
    ps = body.find_all('p')
    with open(link_out, 'w', encoding='utf8') as f:
        for p in ps:
            f.write(p.text + '\n')