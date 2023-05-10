import os
import random
import socket
import sys

MAX_LINE = 2048

class Server:
    def __init__(self, host_, port_):
        self._host = host_
        self._port = port_

        if not os.path.exists('server_files'):
            os.mkdir('server_files')

        if not os.path.exists('server_files/received'):
            os.mkdir('server_files/received')

    def create_packet(self, packet, content, flags=None):
        if flags is None:
            flags = []
        joined_flags = ', '.join(flags)
        message = f'Packet: {packet}\r\nFlags: {joined_flags}\r\nContent: {content}'.encode('utf-8')
        return message

    def parse_message(self, message):
        message = message.decode('utf-8').split('\r\n')
        packet = int(message[0].split(': ')[1])
        flags = message[1].split(': ')[1].split(', ')
        content = '\r\n'.join(message[2 : ])[9 : ]
        return packet, flags, content

    def serve_forever(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        filename = 'server_files/received/default.txt'
        expected = 0

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.setblocking(False)

            while True:
                try:
                    message, address = server_sock.recvfrom(MAX_LINE)
                    packet, flags, content = self.parse_message(message)
                    print(f'Received packet {packet}')
                    if 'BEG' in flags:
                        print('--------Connection established-------------')
                        expected = 0
                        filename = 'server_files/received/' + content
                        if os.path.exists(filename):
                            os.remove(filename)

                    if packet == expected:
                        expected += 1
                        if 'BEG' not in flags:
                            with open(filename, 'a') as f:
                                f.write(content)

                    if random.randint(0, 9) >= 2:
                        server_sock.sendto(self.create_packet(expected - 1, '', flags=['ACK']), address)
                        print(f'ACK sent for packet {packet}, next expected packet {expected}')
                    else:
                        print(f'ACK for packet {packet} lost')

                except BlockingIOError:
                    pass

        except Exception as e:
            print(f'An error occurred {e}!')

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])

    server = Server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass