from flask import Flask, render_template, request
from sender_smtp import SenderServer

app = Flask(__name__)


@app.route('/',methods=['GET', 'POST'])
def form():
    if request == 'POST':

        message = {
            "sender": request.form.get('email_from'),
            "recipient": request.form.get('email_to'),
            "message": request.form.get('message'),
            "file_path": request.form.get('file_path')
        }

        sender = SenderServer(message)
        sender.send_email()
        sender.upload_file()

        return 'Form Submitted!'

    return render_template('form.html')


if __name__ == '__main__':
    app.run(debug=True)
