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


async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=HEADERS) as response:
            return await response.text()


async def parse_data(url):
    try:
        response = await send_request(url)
        soup = BeautifulSoup(response, 'lxml')
        # pagination_block = soup.find('ul', class_='pagination')
        # pages = pagination_block.find_all('a', class_='pagination-link')[-1].text.strip()

        all_flowers_dict = {}

        for page in range(1, 4):
            page_response = await send_request(BASE_URL + f'page={page}')

            soup = BeautifulSoup(page_response, 'lxml')

            all_products_href = soup.find_all('a', class_='product-link')

            for item in all_products_href:
                item_text = item.text
                item_href = 'https://www.agroviola.ru/' + item.get('href')

                all_flowers_dict[item_text.strip()] = item_href
            continue

        with open('all_flowers_dict.json', 'a') as file:
            json.dump(all_flowers_dict, file, indent=4, ensure_ascii=False)

        with open('all_flowers_dict.json') as file:
            all_flowers = json.load(file)

        count = 0

        for name, url in all_flowers.items():
            tmp_name = re.sub(r'\d+', '', name)
            flower_name = tmp_name.replace('(Весна )', '').strip()

            response = await send_request(url)

            soup = BeautifulSoup(response, 'lxml')

            try:
                description = soup.find(id='product-description').find(class_='tab-block-inner editor').text.strip()

                data.append(
                    {
                        'name': flower_name,
                        'description': description
                    }
                )

            except AttributeError:
                data.append(
                    {
                        'name': flower_name,
                        'description': None
                    }
                )

            count += 1
    except Exception as e:
        print(f'Возникла ошибка {e}')


def main():
    try:
        asyncio.run(parse_data(url=BASE_URL))

        with open(f'data/flowers.json', 'a', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    except aiohttp.client_exceptions.ClientConnectorError as e:
        print(f'Возникла ошибка: {e}')


if __name__ == '__main__':
    main()
