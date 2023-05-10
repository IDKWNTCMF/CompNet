import socket
import sys

MAX_LINE = 2048


class Server:
    def __init__(self, host_, port_):
        self._socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host_, port_))
        self._socket.listen()

    def serve_forever(self):
        while True:
            conn, addr = self._socket.accept()
            message = conn.recvfrom(MAX_LINE)[0].decode('utf-8')
            print(f'{message} -> ', end='')
            message = message.upper()
            print(f'{message}')
            conn.send(message.encode('utf-8'))


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    server = Server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass