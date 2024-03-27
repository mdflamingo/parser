import requests
from bs4 import BeautifulSoup

page = requests.get('https://www.agroviola.ru/collection/vegetativnye-cherenki-vesna-2022g')

soup = BeautifulSoup(page.text, 'lxml')

product_cards = soup.find_all(class_="product-card-inner")

with open('flower.txt', 'w') as f:
    for card in product_cards:
        flower = card.text.strip().replace('Подробнее', '').replace('Товар отсутствует','').split('    ')
        f.write(flower[-1] + '\n')
