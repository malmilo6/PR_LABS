import base64
import socket
import threading
import json
import os
import time

CLIENT_MEDIA = 'CLIENT_MEDIA'
HOST = '127.0.0.1'
PORT = 6666

file_parts = []
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((HOST, PORT))


def message_handler():
    while True:
        message = client_socket.recv(1024).decode('utf-8')

        if not message:
            break

        message = json.loads(message)

        if message['type'] == 'connection':
            print(f"Connection received: {message['payload']['message']}")

        elif message['type'] == 'notification':
            print(f"Message received: {message['payload']['text']}")


client_thread = threading.Thread(target=message_handler)
client_thread.daemon = True
client_thread.start()

connection_room = str(input('Room: '))
client_name = str(input('Name: '))

message = {
    "type": "connect",
    "payload": {
        "room": connection_room,
        "name": client_name
    }
}

client_socket.send((json.dumps(message)).encode('utf-8'))


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


while True:

    client_message = input()

    if client_message.upper() == 'EXIT':
        break

    mess = {
        "type": "notification",
        "payload": {
            "room": connection_room,
            "text": client_message,
            "sender": client_name
        }
    }

    if client_message.split(' ')[0] == 'upload:':
        file_path = client_message.split(' ')[1]
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
                msg = {
                    "type": "upload",
                    "payload": {
                        "filename": os.path.basename(file_path),
                        "sender": client_name,
                    }
                }

                client_socket.send(json.dumps(msg).encode('utf-8'))
                parts = chunks(file_data, 128)
                time.sleep(0.05)

                for part in parts:
                    msg = {
                        "type": "upload_chunk",
                        "payload": {
                            "chunk": part
                        }
                    }

                    client_socket.send(json.dumps(msg).encode('utf-8'))
                    time.sleep(0.05)
                time.sleep(0.05)

                msg = {
                    "type": "upload_end",
                    "payload": {
                        "sender": client_name
                    }
                }

                client_socket.send(json.dumps(msg).encode('utf-8'))
        else:
            print(f"File {os.path.basename(file_path)} doesn't exist.")

    elif client_message.split(' ')[0] == 'download:':

        filename = client_message.split(":", 1)[1].strip()
        print(filename)
        if not os.path.exists(CLIENT_MEDIA):
            os.mkdir(CLIENT_MEDIA)
        msg = {
            "type": "download",
            "payload": {
                "filename": filename
            }
        }
        client_socket.send(json.dumps(msg).encode('utf-8'))

    elif message['type'] == 'download_chunk':
        chunk = message['payload']["chunk"]
        file_parts.append(base64.b64decode(chunk))

    elif message['type'] == 'download_end':
        filename = message['payload']['filename']
        with open(os.path.join(CLIENT_MEDIA, filename), 'wb') as f:
            f.write(b''.join(file_parts))
        notification = {
            "type": "notification",
            "payload": {
                "text": f"User {client_name} downloaded the file: {filename}"
            }
        }
        client_socket.send(json.dumps(notification).encode('utf-8'))

    client_socket.send(json.dumps(mess).encode('utf-8'))

client_socket.close()
