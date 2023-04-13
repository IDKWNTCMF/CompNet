import sys
import time
import socket
import datetime

import numpy as np


MAX_LINE = 2048
PACKETS = 10


class Client:
    def __init__(self, server_host_, server_port_, client_host_, client_post_):
        self._server_host = server_host_
        self._server_port = server_port_
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_sock.bind((client_host_, client_post_))

        self.rtts = []


    def send_message(self, message):
        try:
            self.client_sock.settimeout(1)
            send_time = time.time()
            self.client_sock.sendto(message.encode(), (self._server_host, self._server_port))

            while True:
                received = self.client_sock.recv(MAX_LINE)
                if len(received) != 0:
                    recv_time = time.time()
                    print(received.decode())
                    self.rtts.append(1000 * (recv_time - send_time))
                    print(f'RTT CUR/MIN/AVG/MAX = {self.rtts[-1]:.3f}/{np.min(self.rtts):.3f}/{np.mean(self.rtts):.3f}/{np.max(self.rtts):.3f} ms')

                    break

        except socket.timeout:
            print('Request timed out')
        finally:
            print('---------------------------------------')


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    client_host = sys.argv[3]
    client_port = int(sys.argv[4])

    client = Client(server_host, server_port, client_host, client_port)

    for i in range(PACKETS):
        cur_time = datetime.datetime.now().strftime('%H:%M:%S')
        client.send_message(f'Ping {i + 1} {cur_time}')

    print('--- ping statistics ---')
    print(f'{PACKETS} packets transmitted, {len(client.rtts)} received, {100 * (1 - len(client.rtts) / PACKETS):.3f}% packet loss')
    print(f'RTT MIN/AVG/MAX = {np.min(client.rtts):.3f}/{np.mean(client.rtts):.3f}/{np.max(client.rtts):.3f} ms')
