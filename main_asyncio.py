import re
import time

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

    url = f'https://www.agroviola.ru/collection/albom-vse-sorta?{page}='

    async with session.get(url=url, headers=HEADERS) as response:
        response_text = await response.text()

        # with open('index.html', 'w') as file:
        #     file.write(response_text)
        #
        # with open('index.html') as file:
        #     src = file.read()

        soup = BeautifulSoup(response_text, 'lxml')

        all_flowers_href = soup.find_all('a', class_="product-link")

        all_flowers_dict = {}

        for item in all_flowers_href:
            item_text = item.text
            item_href = 'https://www.agroviola.ru/' + item.get('href')

            all_flowers_dict[item_text.strip()] = item_href

        with open('all_categories_dict.json', 'w') as file:
            json.dump(all_flowers_dict, file, indent=4, ensure_ascii=False)

        with open('all_categories_dict.json') as file:
            all_flowers = json.load(file)

        count = 0

        for name, url in all_flowers.items():
            result_string = re.sub(r'\d+', '', name)
            category_name_final = result_string.replace('(Весна )', '').strip()

            async with session.get(url=url, headers=HEADERS) as response:
                response = await response.text()

                # with open(f'data/{count}_{category_name_final}.html', 'w') as file:
                #     file.write(src)
                #
                # with open(f'data/{count}_{category_name_final}.html') as file:
                #     src = file.read()
                # cобираем заголовки и проверяем наличие "Описание"
                soup = BeautifulSoup(response, 'lxml')

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
        # pagination_block = soup.find('ul', class_='pagination')
        # pages = pagination_block.find_all('a', class_='pagination-link')[-1].text.strip()

        tasks = []

        for page in range(1, 3):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    try:
        asyncio.run(gather_data())
        finish_time = time.time() - start_time

        with open(f'data/flowers.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f'Затраченное время на работу скрипта: {finish_time}')
    except Exception as e:
        with open(f'data/flowers.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f'Возникла ошибка: {e}')


if __name__ == '__main__':
    main()
