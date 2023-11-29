import json
import requests
from bs4 import BeautifulSoup
import pika
import threading
import psycopg2

def clear_queue(queue_name):
    connection_params = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_purge(queue_name)
    print(f"Queue {queue_name} cleared.")
    connection.close()


def insert_url_into_db(data):
    db_params = {
        'database': 'postgres',
        'user': 'postgres',
        'password': 'mysecretpassword',
        'host': 'localhost',
        'port': 5432
    }

    # Connect to the PostgreSQL server
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    description = data['Description']
    prices = str(data['Prices'])

    # Insert into the database
    try:
        cur.execute("INSERT INTO cars (description, Prices) VALUES (%s, %s)", (description, prices))
        conn.commit()
        print(f"Inserted data...")
    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def scrape_product(url):
    data = {}
    page = requests.get(f'{url}')
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find product description
    for div in soup.find('div', {'class': 'adPage__content__description grid_18'}):
        data['Description'] = div.text

    h2 = soup.find('div', {'class': 'adPage__content__features'}).find_all('h2')

    # Product features
    for h in h2:
        span_t = {}
        ul = h.find_next('ul')
        if ul:
            li_l = ul.find_all('li')
            if li_l:
                for li in li_l:
                    span_elements = li.find_all('span')
                    # span_t = [span.text for span in span_elements]
                    feat = li.find_all('span')
                    if len(feat) == 2:
                        span_t[feat[0].text] = feat[1].text
                    else:
                        span_t[feat[0].text] = 'None'
        data[h.text] = span_t

    # Extract sub_category
    sub_cat = soup.find('div', {'class': 'adPage__content__features adPage__content__features__category'})
    for h2 in sub_cat.find('h2'):
        next_div = h2.find_next('div')
        if next_div:
            a = next_div.find('a')
            data[h2] = a.text

    # Prices
    pr = soup.find('div', {'class': 'js-phone-content adPage__content__footer__item'})
    li = pr.find_all('li')
    price_data = {}
    for price in li:
        price_value = price.find('span', itemprop="price")
        price_currency = price.find('span', itemprop="priceCurrency")
        if price_currency and price_value:
            price_data[price_value.text] = price_currency.text
    data['Prices'] = price_data

    # Region && Contacts
    reg = soup.find_all('dl', {'class': 'adPage__content__region grid_18'})
    rc = {}
    for d in reg:
        dds = d.find_all_next('dd')
        rc['Region'] = (dds[0].text + '' + dds[1].text).replace(' ', '')
        rc['Contacts'] = d.find_next('a')['href']

    data['Region&&Contacts'] = rc

    return data


def start_consumer(consumer_id, queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.queue_bind(exchange='logs', queue=queue_name)

    print(f'Consumer {consumer_id} is waiting... ')

    def callback(ch, method, properties, body):
        body = body.decode('utf-8')
        urls = json.loads(body)
        for url in urls:
            try:
                data = scrape_product(url)
                insert_url_into_db(data)
                print(f'Consumer {consumer_id} processed URL: {url}')
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()


queue_name = 'shared_queue'
clear_queue(queue_name)
num_consumers = 2
for i in range(num_consumers):
    thread = threading.Thread(target=start_consumer, args=(i + 1, queue_name))
    thread.start()
