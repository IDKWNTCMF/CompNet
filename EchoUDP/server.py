import socket
import random
import sys
import time

MAX_LINE = 2048


class Server:
    def __init__(self, host_, port_, timeout_):
        self._host = host_
        self._port = port_
        self._timeout = timeout_

    def serve_forever(self):
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.setblocking(False)
            connections = dict()

            while True:
                try:
                    message, address = server_sock.recvfrom(MAX_LINE)
                    if address not in connections:
                        print(f'Established connection with {address}')

                    connections[address] = time.time()

                    if random.randint(0, 9) >= 2:
                        response = message.upper()
                        print(f'{message.decode()} -> {response.decode()} (address: {address})')
                        server_sock.sendto(message, address)
                    else:
                        print('Message lost')

                except BlockingIOError:
                    closed_connections = set()
                    for address, t in connections.items():
                        cur_time = time.time()
                        if cur_time - t > self._timeout:
                            closed_connections.add(address)
                    if len(closed_connections) != 0:
                        for address in closed_connections:
                            print(f'Connection with address: {address} closed')
                            connections.pop(address)

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            server_sock.close()


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[3])

    server = Server(host, port, timeout)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass