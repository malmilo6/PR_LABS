import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class SenderServer:
    def __init__(self, email_config):
        self.sender = 'cocostarcandrei84@gmail.com'
        self.recipient = email_config['recipient']
        self.body = email_config['message']
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.username = 'cocostarcandrei84@gmail.com'
        self.password = 'wxxo mbqa nims qbqo'
        self.file_path = email_config['file_path']
        self.ftp_host = '138.68.98.108'
        self.ftp_port = 21
        self.ftp_username = 'yourusername'
        self.ftp_pass = 'yourusername'
        self.target_path = self.file_path.split('/')[-1]
        self.ftp_instance = None

    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg['Subject'] = 'Hello from COCOSTARCU ANDREI!'

        msg.attach(MIMEText(self.body, 'plain'))

        file_path = self.file_path
        filename = file_path.split('/')[-1]

        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp_server:
                smtp_server.ehlo()
                smtp_server.starttls()
                smtp_server.login(self.username, self.password)
                smtp_server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def ftp_connection(self):
        ftp = FTP()
        ftp.connect(self.ftp_host, self.ftp_port)
        ftp.login(self.ftp_username, self.ftp_pass)
        self.ftp_instance = ftp

    def upload_file(self):
        try:
            self.ftp_connection()
            with open(self.file_path, 'rb') as file:
                self.ftp_instance.storbinary(f'STOR {self.target_path}', file)
            self.ftp_instance.quit()
            print('File uploaded successfully!')
        except Exception as e:
            print(f'Failed to upload the file: {e}')

