import datetime
import socket
import sys
from time import sleep

class Server:
    def __init__(self, port_):
        self._port = port_

    def serve_forever(self):
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            while True:
                time = str(datetime.datetime.now())
                print(time)
                server_sock.sendto(time.encode('utf-8'), ('<broadcast>', self._port))
                sleep(1)

        except Exception as e:
            print(f'An error occurred: {e}')

        finally:
            server_sock.close()

if __name__ == '__main__':
    port = int(sys.argv[1])

    server = Server(port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass