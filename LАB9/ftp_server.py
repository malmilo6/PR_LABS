from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

PATH = '/LАB9/local/remote_storage'


def setup_ftp_server():
    authorizer = DummyAuthorizer()

    authorizer.add_user('user', '12345', PATH, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    handler.banner = "pyftpdlib based ftpd ready."

    address = ('127.0.0.1', 6699)
    server = FTPServer(address, handler)

    server.serve_forever()


if __name__ == "__main__":
    setup_ftp_server()
