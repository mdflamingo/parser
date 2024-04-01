import re

import requests
from bs4 import BeautifulSoup
import json


base_url = 'https://www.agroviola.ru/collection/albom-vse-sorta?'

headers = {
    'Accept': 'text/css,*/*;q=0.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


for page in range(1, 3):

    response = requests.get(base_url + 'page=' + str(page), headers=headers)
    status_code = response.status_code

    src = response.text

    with open('index.html', 'w') as file:
        file.write(src)

    with open('index.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    # page_count = soup.find(class_='pagination-wrapper').find('ul').text
    # print(page_count.strip()[-1])

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
    data = []
    for category_name, category_href in all_categories.items():
        result_string = re.sub(r'\d+', '', category_name)
        category_name_final = result_string.replace('(Весна )', '').strip()

        response = requests.get(url=category_href, headers=headers)
        src = response.text

        with open(f'data/{count}_{category_name_final}.html', 'w') as file:
            file.write(src)

        with open(f'data/{count}_{category_name_final}.html') as file:
            src = file.read()
        # cобираем заголовки и проверяем наличие "Описание"
        soup = BeautifulSoup(src, 'lxml')

        try:
            description = soup.find(id='product-description').find(class_='tab-block-inner editor').text.strip()

            data.append(
                {
                    'name': category_name_final,
                    'description': description
                }
            )

            with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except AttributeError:
            data.append(
                {
                    'name': category_name_final,
                    'description': None
                }
            )

            with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        count += 1

        continue
