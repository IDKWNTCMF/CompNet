import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib
import sys

class Sender:
    def __init__(self, from__, password_filename_):
        self._from = from__
        self._password = open(password_filename_).read()

    def send_mail(self, to_, subject_, filename_):
        msg = MIMEMultipart()
        content = open(filename_).read()

        msg['From'] = self._from
        msg['To'] = to_
        msg['Subject'] = subject_

        if filename_.endswith('.txt'):
            msg.attach(MIMEText(content, 'plain'))
        elif filename_.endswith('.html'):
            msg.attach(MIMEText(content, 'html'))
        else:
            print('Wrong format of input file')
            return

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(self._from, self._password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

        print('Successfully sent')

if __name__ == '__main__':
    from_ = sys.argv[1]
    password_filename = sys.argv[2]
    to = sys.argv[3]
    subject = sys.argv[4]
    filename = sys.argv[5]

    sender = Sender(from_, password_filename)
    sender.send_mail(to, subject, filename)