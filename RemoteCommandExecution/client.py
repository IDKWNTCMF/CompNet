import sys
import socket

MAX_LINE = 2048


class Client:
    def __init__(self, host_, port_):
        self._host = host_
        self._port = port_
    def send_command(self, command_):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_sock.connect((self._host, self._port))

        try:
            client_sock.sendall(command_.encode('utf-8'))

            while True:
                data = client_sock.recv(MAX_LINE)
                if not data:
                    break
                print(data.decode(), flush=True, end='')

        finally:
            client_sock.close()


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    command = sys.argv[3]

    client = Client(host, port)
    try:
        client.send_command(command)
    except KeyboardInterrupt:
        pass