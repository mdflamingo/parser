from bs4 import BeautifulSoup
import aiohttp
import asyncio
import json
import re


BASE_URL = f'https://www.agroviola.ru/collection/albom-vse-sorta?'

HEADERS = {
    'Accept': 'text/css,*/*;q=0.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

data = []


async def get_page_data(session, page):
    url = f'https://www.agroviola.ru/collection/albom-vse-sorta?{page}'

    async with session.get(url=url, headers=HEADERS) as response:
        response_text = await response.text()

        with open(f'data_html/{page}.html', 'w')as file:
            file.write(response_text)

        with open(f'data_html/{page}.html') as file:
            src = file.read()

        soup = BeautifulSoup(src, 'lxml')

        all_products_href = soup.find_all(class_="product-link")
        all_products_dict = {}

        for item in all_products_href:
            item_text = item.text
            item_href = 'https://www.agroviola.ru/' + item.get('href')

            all_products_dict[item_text.strip()] = item_href


async def gather_data():
    async with aiohttp.ClientSession() as session:

        tasks = []

        for page in range(1, 10):
            tasks.append(get_page_data(session, page))
        return await asyncio.gather(*tasks)


def main():
    try:
        asyncio.run(gather_data())
        # with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
        #     json.dump(data, file, indent=4, ensure_ascii=False)
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print(f'Возникла ошибка: {e}')


if __name__ == '__main__':
    main()
