import socket
import sys


MAX_LINE = 2048

class Client:
    def __init__(self, port_, name_):
        self._port = port_
        self._name = name_

    def start_client(self):
        client_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )

        try:
            client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client_sock.bind(('', self._port))

            while True:
                data, _ = client_sock.recvfrom(MAX_LINE)
                if data:
                    print(f'Client {self._name} received: {data.decode()}')

        except Exception as e:
            print(f'An error occurred: {e}')

        finally:
            client_sock.close()


if __name__ == '__main__':
    port = int(sys.argv[1])
    name = sys.argv[2]

    client = Client(port, name)
    try:
        client.start_client()
    except KeyboardInterrupt:
        pass