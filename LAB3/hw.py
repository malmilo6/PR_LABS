import json

import requests
from bs4 import BeautifulSoup
from pprint import pprint


def scrape_product(url):
    data = {}
    page = requests.get(f'{url}')
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get owner info
    owner_info = {}
    oi = soup.find('dl', {'class': 'adPage__aside__stats__owner'})
    owner_info['Name'] = oi.find('a', {'class': 'adPage__aside__stats__owner__login buyer_experiment'}).text
    owner_info['On website since'] = oi.find('span').text
    last_upd = oi.find_next('div')
    owner_info['Last Update'] = last_upd.text
    add_type = last_upd.find_next('div')
    owner_info['Add type'] = add_type.text
    views = add_type.find_next('div')
    owner_info['Views'] = views.text

    data['Owner info'] = owner_info

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
    reg = soup.find_all('dl',{'class': 'adPage__content__region grid_18'})
    rc = {}
    for d in reg:
        dds = d.find_all_next('dd')
        rc['Region'] = (dds[0].text + '' + dds[1].text).replace(' ', '')
        rc['Contacts'] = d.find_next('a')['href']

    data['Region&&Contacts'] = rc

    return data


if __name__ == '__main__':
    url_product = 'https://999.md/ro/82806968'
    product_data = scrape_product(url_product)
    pprint(product_data)
    with open("data.txt", "w") as outfile:
        outfile.write(json.dumps(product_data, indent=2, ensure_ascii=False))