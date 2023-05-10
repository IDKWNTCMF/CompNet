import socket
import sys

MAX_LINE = 2048


class Client:
    def __init__(self, server_host_, server_port_):
        self._server_host = server_host_
        self._server_port = server_port_
        self._socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    def send_message(self, message):
        print(f'{message} -> ', end='')
        self._socket.connect((self._server_host, self._server_port))
        self._socket.send(message.encode('utf-8'))
        response, addr = self._socket.recvfrom(MAX_LINE)
        print(response.decode('utf-8'))


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    message = sys.argv[3]
    client = Client(server_host, server_port)
    try:
        client.send_message(message)
    except KeyboardInterrupt:
        pass