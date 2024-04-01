import re
import time

import requests
from bs4 import BeautifulSoup
import json
import asyncio
import aiohttp


BASE_URL = 'https://www.agroviola.ru/collection/albom-vse-sorta?'

HEADERS = {
    'Accept': 'text/css,*/*;q=0.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

data = []
start_time = time.time()


async def get_page_data(session, page):
    """Получение данных страниц. Пробегает по каждой странице и собирает данные"""

    url = f'https://www.agroviola.ru/collection/albom-vse-sorta?{page}'

    async with session.get(url=url, headers=HEADERS) as response:
        response_text = await response.text()

        with open('index.html', 'w') as file:
            file.write(response_text)

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

        for category_name, category_href in all_categories.items():
            result_string = re.sub(r'\d+', '', category_name)
            category_name_final = result_string.replace('(Весна )', '').strip()

            response = requests.get(url=category_href, headers=HEADERS)
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

            except AttributeError:
                data.append(
                    {
                        'name': category_name_final,
                        'description': None
                    }
                )

            count += 1
        print(f'[INFO] Обрабатывается страница {page}')


async def gather_data():
    """Сбор даннных"""
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=BASE_URL, headers=HEADERS)
        soup = BeautifulSoup(await response.text(), 'lxml')
        # page_count = int(soup.find('ul', class_='pagination').find_all('li'))

        tasks = []

        for page in range(1, 10):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())
    finish_time = time.time() - start_time

    with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f'Затраченное время на работу скрипта: {finish_time}')


if __name__ == '__main__':
    main()
