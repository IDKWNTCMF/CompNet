import socket
import sys

from ftplib import FTP


MAX_LINE = 2048


class FTPClient:
    def __init__(self, host_, port_, username_, password_filename_):
        self._host = host_
        self._port = port_
        self._username = username_
        self._password = open(password_filename_).read()

    def process_query(self, query_, arg_):
        ftp = FTP()
        ftp.connect(self._host, self._port)
        ftp.login(self._username, self._password)

        if query_ == 'ls':
            files = ftp.nlst(arg_)
            for file in files:
                print(file)
        elif query_ == 'upload':
            with open(arg_, 'rb') as file:
                ftp.storlines(f'STOR {arg_}', file)
            print(f'File {arg_} uploaded successfully')
        elif query_ == 'download':
            with open(arg_, 'wb') as file:
                response = ftp.retrbinary(f'RETR {arg_}', file.write)

                if response.startswith('226'):
                    print(f'File {arg_} downloaded successfully')
                else:
                    print(f'Error occurred while downloading. Local file may be corrupt')

        ftp.close()


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password_filename = sys.argv[4]
    query = sys.argv[5]
    arg = sys.argv[6]

    client = FTPClient(host, port, username, password_filename)
    client.process_query(query, arg)