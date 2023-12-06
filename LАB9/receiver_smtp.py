import smtpd
import asyncore
import ftplib


class ReceiverSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print('Receiving message from:', peer)
        print('From:', mailfrom)
        print('To:', rcpttos)
        print('Message:', data)
        return '250 Ok'


server_address = ('127.0.0.1', 1025)  # Run on localhost, port 1025
smtp_server = ReceiverSMTPServer(server_address, None)

print("SMTP server running on port 1025")
asyncore.loop()
