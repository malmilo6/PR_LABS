import socket
import regex as reg

product_data = [
    {
        "id": 1,
        "name": "Fluent Python: Clear, Concise, and Effective Programming",
        "author": "Luciano Ramalho",
        "description": "Don't waste time bending Python to fit patterns you've learned in other languages. Python's simplicity lets you become productive quickly, but often this means you aren't using everything the language has to offer. With the updated edition of this hands-on guide, you'll learn how to write effective, modern Python 3 code by leveraging its best ideas. "
    },
    {
        "id": 2,
        "name": "Introducing Python: Modern Computing in Simple Packages",
        "author": "Bill Lubanovic",
        "description": "Easy to understand and fun to read, this updated edition of Introducing Python is ideal for beginning programmers as well as those new to the language. Author Bill Lubanovic takes you from the basics to more involved and varied topics, mixing tutorials with cookbook-style code recipes to explain concepts in Python 3. End-of-chapter exercises help you practice what you’ve learned."
    }
]

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")


def handle_request(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    print(request_line)
    path = request_line[1]

    response_content = ''
    status_code = 200

    if path == '/':
        with open('html_content/welcome.html') as home_page:
            response_content = home_page.read()

    elif path == '/about':
        with open('html_content/about.html') as about_page:
            response_content = about_page.read()
    elif path == '/home':
        with open('html_content/home.html') as home_page:
            response_content = home_page.read()
    elif path == '/products':
        with open('html_content/products.html') as products_page:
            response_content = products_page.read()
        for product in product_data:
            response_content += f"<a href='/product/{product['id']}'> Product: {product['name']} </a><br>"
    elif reg.match(r"/product/[0-9]+", path):
        product_id = int(reg.split(r"/", path)[2])

        for product in product_data:
            if product['id'] == product_id:
                response_content = f"""
                <h2>Product review</h2>
                <ul>
                        <li>
                            <span>Product ID: </span>
                            <span>{product['id']}</span>
                        </li>
                        <li>
                            <span>Product name: </span>
                            <span>{product['name']}</span>
                        </li>
                        <li>
                            <span>Product author: </span>
                            <span>{product['author']}</span>
                        </li>
                        <li>
                            <span>Product description: </span>
                            <span>{product['description']}</span>
                        </li>   
                                          
                </ul>
                """

    else:
        with open('html_content/not_found.html') as products_page:
            response_content = products_page.read()

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    client_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    try:
        handle_request(client_socket)
    except KeyboardInterrupt:
        pass
