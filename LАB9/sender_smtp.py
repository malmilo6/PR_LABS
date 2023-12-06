import smtplib
from ftplib import FTP

FTP_SERVER = '127.0.0.1'
FTP_PORT = 6699
FTP_USERNAME = 'user'
FTP_PASSWORD = '12345'
SMTP_SERVER = '127.0.0.1'
SMTP_PORT = 1025
FILE_PATH = '/home/malmilo/Uni/PR_LABS_TASKS/LАB9/local_storage/'


class SenderServer:
    def __init__(self, email):
        self.sender = email['sender']
        self.recipient = email['recipient']
        self.message = email['message']
        self.smtp_port = SMTP_PORT
        self.smtp_server = SMTP_SERVER
        self.ftp_host = FTP_SERVER
        self.ftp_port = FTP_PORT
        self.ftp_username = FTP_USERNAME
        self.ftp_pass = FTP_PASSWORD
        self.file_path = email['file_path']
        self.target_path = self.file_path.split('/')[-1]
        self.ftp_instance = None

    def send_email(self):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.sendmail(self.sender, [self.recipient], self.message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def ftp_connection(self):
        ftp = FTP()
        ftp.connect(self.ftp_host, self.ftp_port)
        ftp.login(self.ftp_username, self.ftp_pass)
        self.ftp_instance = ftp

    def upload_file(self):
        self.ftp_connection()

        with open(self.file_path, 'rb') as file:
            self.ftp_instance.storbinary(f'STOR {self.target_path}', file)

