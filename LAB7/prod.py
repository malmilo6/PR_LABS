import json

import pika
import sys
from bs4 import BeautifulSoup
import requests


def connection_est(message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    message = (json.dumps(message)).encode('utf-8')
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(f" [x] Sent {message}")
    connection.close()


def scrap_999(url, urls=None):
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
            next = nav.find_next_sibling()
            a = next.find('a')
            href = a.get('href')
            next_page = f'https://999.md{href}'
            connection_est(urls)
            scrap_999(next_page, [])
        else:
            return
    return urls


url = 'https://999.md/ru/list/transport/cars'
urls = scrap_999(url, [])

