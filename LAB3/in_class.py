import json

import requests
from bs4 import BeautifulSoup


def scrap_999(url, urls=None, max_page_num=None):
    if urls is None:
        urls = []
    page = requests.get(f'{url}')
    soup = BeautifulSoup(page.content, 'html.parser')
    for h in soup.find_all('li', {'class': 'ads-list-photo-item'}):
        a = h.find('a')
        try:
            if 'href' in a.attrs:
                url = a.get('href')
                if 'booster' not in url:
                    abs_url = f'https://999.md{url}'
                    print(abs_url)
                    urls.append(abs_url)
                else:
                    pass
        except:
            pass
    for n in soup.find_all('nav', {'class': 'paginator cf'}):
        nav = n.find('li', {'class': 'current'})
        if nav.find_next_sibling():
            if max_page_num:
                max_page_num -= 1
            next = nav.find_next_sibling()
            a = next.find('a')
            href = a.get('href')
            next_page = f'https://999.md{href}'
            scrap_999(next_page, urls, None)
        else:
            return
    return urls


if __name__ == '__main__':
    url = 'https://999.md/ru/list/phone-and-communication/drones'
    urls = scrap_999(url, [], None)
    with open("urls.txt", "w") as outfile:
       outfile.write(json.dumps(urls, indent=2))

