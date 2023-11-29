from bs4 import BeautifulSoup
import requests
from pprint import pprint
import json

url = 'http://localhost:8080/products'
p = requests.get(url)

soup = BeautifulSoup(p.content, 'html.parser')
print(p.content)

list_of_products = soup.find_all('a')

list_of_product_dicts = []
for product in list_of_products:
    href = product['href']
    product_lint = f'http://localhost:8080{href}'
    req = requests.get(product_lint)
    sp = BeautifulSoup(req.content, 'html.parser')
    ul = sp.find('ul')
    lis = ul.find_all('li')
    product_dict = {}

    for li in lis:
        key = li.find_next('span')
        value = key.find_next('span')
        product_dict[key.text] = value.text

    list_of_product_dicts.append(product_dict)

# with open("website_content.txt", "w") as outfile:
#     outfile.write(json.dumps(list_of_product_dicts, indent=2, ensure_ascii=False))

pprint(list_of_product_dicts)