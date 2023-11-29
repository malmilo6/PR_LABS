import base64
import socket
import threading
import json
import os
import time

HOST = '127.0.0.1'
PORT = 6666
file_parts = []
file_name = ''

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

server_rooms = {}
server_clients = []

SERVER_MEDIA = "SERVER_MEDIA"


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def client_handler(client_socket, client_address):
    print(f'Connection from {client_address}')

    while True:
        client_message = client_socket.recv(1024).decode('utf-8')

        if not client_message:
            break

        print(f'Message: {client_message}, from {client_address} ')

        print(client_message)
        message = json.loads(client_message)

        if message['type'] == 'connect':
            room_name = message['payload']['room']
            if room_name not in server_rooms:
                server_rooms[room_name] = [client_socket]
            else:
                server_rooms[room_name].append(client_socket)

            for client in server_rooms[message['payload']['room']]:
                resp = {
                    "type": "connection",
                    "payload": {
                        "message": f"Client {message['payload']['name']} has been connected "
                                   f"to the {message['payload']['room']}."
                    }
                }
                client.send(json.dumps(resp).encode('utf-8'))
        elif message['type'] == 'message':
            for client in server_rooms[message['payload']['room']]:
                notification = {
                    "type": "notification",
                    "payload": {
                        "text": message['payload']['text']
                    }
                }
                client.send(json.dumps(notification).encode('utf-8'))

        elif message['type'] == 'upload':
            if not os.path.exists(SERVER_MEDIA):
                os.makedirs(SERVER_MEDIA)
            file_name = message['payload']['filename']
            # notification = {
            #     "type": "notification",
            #     "payload": {
            #         "text": f"User {message['payload']['sender']} uploaded the {filename} file."
            #     }
            # }
            # client_socket.send(json.dumps(notification).encode('utf-8'))

        elif message['type'] == 'upload_chunk':
            chunk = message['payload']['chunk']
            file_parts.append(base64.b64decode(chunk))

        elif message['type'] == 'upload_end':
            file_name = message['payload']['filename']
            with open(os.path.join(SERVER_MEDIA, file_name), 'wb') as f:
                f.write(b''.join(file_parts))
            notification = {
                "type": "notification",
                "payload": {
                    "text": f"User {message['payload']['sender']} uploaded the {file_name} file."
                }
            }
            client_socket.send(json.dumps(notification).encode('utf-8'))

        elif message['type'] == 'download':
            file_name = message['payload']['filename']
            file_path = os.path.join(SERVER_MEDIA, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode()
                    msg = {
                        "type": "download",
                        "payload": {
                            "filename": file_name
                        }
                    }

                    client_socket.send(json.dumps(msg).encode('utf-8'))
                    parts = chunks(file_data, 128)
                    time.sleep(0.05)

                    for part in parts:
                        msg = {
                            "type": "download_chunk",
                            "payload": {
                                "chunk": part
                            }
                        }
                        client_socket.send(json.dumps(msg).encode('utf-8'))
                        time.sleep(0.05)
                    time.sleep(0.05)
                    msg = {
                        "type": "download_end",
                        "payload": {
                            "sender": 'server'
                        }
                    }
                    client_socket.send(json.dumps(msg).encode('utf-8'))

                notification = {
                    "type": "notification",
                    "payload": {
                        "text": f"The file {file_name} has been downloaded and removed from the server."
                    }
                }
                client_socket.send(json.dumps(notification).encode('utf-8'))

            else:
                error_msg = {
                    "type": "error",
                    "payload": {
                        "text": f"The {file_name} doesn't exist."
                    }
                }
                client_socket.send(json.dumps(error_msg).encode('utf-8'))
    client_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    server_clients.append(client_socket)
    client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
    client_thread.start()
