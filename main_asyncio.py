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

    url = f'https://www.agroviola.ru/collection/albom-vse-sorta?page={page}'

    async with session.get(url=url, headers=HEADERS) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        all_flowers_href = soup.find_all('a', class_="product-link")

        all_flowers_dict = {}

        for item in all_flowers_href:
            item_text = item.text
            item_href = 'https://www.agroviola.ru/' + item.get('href')

            all_flowers_dict[item_text.strip()] = item_href

        count = 0

        for name, url in all_flowers_dict.items():
            result_string = re.sub(r'\d+', '', name)
            category_name_final = result_string.replace('(Весна )', '').strip()

            async with session.get(url=url, headers=HEADERS) as response:
                response = await response.text()

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
        pagination_block = soup.find('ul', class_='pagination')
        pages = pagination_block.find_all('a', class_='pagination-link')[-1].text.strip()

        tasks = []

        for page in range(1, int(pages)):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    # try:
    asyncio.run(gather_data())

    with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # except Exception as e:
    #     with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
    #         json.dump(data, file, indent=4, ensure_ascii=False)
      #  print(f'Возникла ошибка: {e}')


if __name__ == '__main__':
    main()
