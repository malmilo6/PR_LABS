import socket
from pprint import pprint
from bs4 import BeautifulSoup
import json

host = socket.gethostbyname("localhost")
port = 8080


def tcp_request(path, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    http_header = f"GET {path} HTTP/1.1\nHost: {host}\n\n"
    s.send(bytes(http_header, "utf-8"))

    raw_data = s.recv(1024)
    head, *body_lines = str(raw_data, "utf-8").split("\n\n")
    body = "\n\n".join(body_lines)
    return body


def get_website_content(req):
    return BeautifulSoup(req, 'html.parser')


def get_hrefs(content):
    a_s = content.find_all('a')
    hrefs = []
    if a_s:
        for a in a_s:
            hrefs.append(a.get('href'))
    else:
        return
    return hrefs


def scrap(start_path, host, port):
    website_content = {}
    page_dict = {}
    items_content = []
    body = tcp_request(start_path, host, port)
    page_content = get_website_content(body)
    page_hrefs = get_hrefs(page_content)
    if page_hrefs is not None:
        for href in page_hrefs:
            curr_page = tcp_request(href, host, port)
            curr_page_content = get_website_content(curr_page)
            page_dict[href] = str(curr_page_content)

            if get_hrefs(curr_page_content):
                hrefs = get_hrefs(curr_page_content)
                for href in hrefs:
                    req = tcp_request(href, host, port)
                    content = get_website_content(req)
                    page_dict[href] = str(content)
                    ul = content.find('ul')
                    lis = ul.find_all('li')
                    product_dict = {}

                    for li in lis:
                        spans = li.find_all_next('span')
                        print(spans)
                        key = spans[0].text
                        value = spans[1].text
                        product_dict[key] = value

                    items_content.append(product_dict)
    website_content['Pages found'] = page_dict
    website_content['Items found'] = items_content
    return website_content


data = scrap('/', host, port)
pprint(data)
with open("website_content.txt", "w") as outfile:
    outfile.write(json.dumps(data, indent=2, ensure_ascii=False))



