import re

import requests
from bs4 import BeautifulSoup
import json
import csv


url = 'https://www.agroviola.ru/collection/albom-vse-sorta'

headers = {
    'Accept': 'text/css,*/*;q=0.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

req = requests.get(url, headers=headers)
src = req.text

with open('index.html', 'w') as file:
    file.write(src)

with open('index.html') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

all_products_href = soup.find_all(class_="product-link")

all_products_dict = {}

for item in all_products_href:
    item_text = item.text
    item_href = 'https://www.agroviola.ru/' + item.get('href')

    all_products_dict[item_text.strip()] = item_href

with open('all_categories_dict.json', 'w') as file:
    json.dump(all_products_dict, file, indent=4, ensure_ascii=False)

with open('all_categories_dict.json') as file:
    all_categories = json.load(file)

count = 0

for category_name, category_href in all_categories.items():
    result_string = re.sub(r'\d+', '', category_name)
    category_name_final = result_string.replace('(Весна )', '').strip()

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f'data/{count}_{category_name_final}.html', 'w') as file:
        file.write(src)

    with open(f'data/{count}_{category_name_final}.html') as file:
        src = file.read()
    # cобираем заголовки и проверяем наличие "Описание"
    soup = BeautifulSoup(src, 'lxml')
    titles = soup.find(class_='tab-block').text.strip()
    print(titles)

    with open(f'data/flowers.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow((
            category_name_final,
            titles
        ))
        count += 1
