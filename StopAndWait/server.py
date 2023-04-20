import socket
import random
import sys
import os

from Checksum.checksum import get_checksum, val_checksum

MAX_LINE = 2048


class Server:
    def __init__(self, host_, port_, timeout_):
        self._host = host_
        self._port = port_
        self._timeout = timeout_

        if not os.path.exists('server_files'):
            os.mkdir('server_files')

        if not os.path.exists('server_files/received'):
            os.mkdir('server_files/received')

    def serve_forever(self):
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        filename = 'server_files/received/default.txt'

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.setblocking(False)

            while True:
                try:
                    message, address = server_sock.recvfrom(MAX_LINE)
                    method, packet, flags, content = self.parse_message(message)
                    print(f'Received packet {packet}')

                    if random.randint(0, 9) >= 2:
                        server_sock.sendto(self.create_packet('', packet, '', flags=['ACK']), address)
                        print(f'ACK sent for packet {packet}')
                        if 'BEG' in flags:
                            print('--------Connection established-------------')
                            if method == 'POST':
                                filename = 'server_files/received/' + content
                                if os.path.exists(filename):
                                    os.remove(filename)
                            if method == 'GET':
                                self.send_file(server_sock, content, address)
                                continue
                        else:
                            with open(filename, 'a') as f:
                                f.write(content)

                except BlockingIOError:
                    pass
                except socket.timeout:
                    pass
                except RuntimeError:
                    print('Checksum is not correct')

        except Exception as e:
            print(f'An error occurred: {e}')

    def create_packet(self, method_, packet, content, flags=None):
        if flags is None:
            flags = []
        joined_flags = ', '.join(flags)
        message = f'Method: {method_}\r\nPacket: {packet}\r\nFlags: {joined_flags}\r\nContent: {content}'.encode('utf-8')
        message = get_checksum(message).to_bytes(2, byteorder='big') + message
        return message

    def parse_message(self, message):
        if not val_checksum(message):
            raise RuntimeError('Checksum validation failed')
        message = message[2 : ].decode('utf-8').split('\r\n')
        method_ = message[0].split(': ')[1]
        packet = int(message[1].split(': ')[1])
        flags = message[2].split(': ')[1].split(', ')
        content = '\r\n'.join(message[3:])[9:]
        return method_, packet, flags, content


    def send_file(self, server_sock, filename_, address):
        try:
            with open(filename_, 'r') as f:
                content = f.read()
                server_sock.settimeout(self._timeout)
                beg = 0
                packet = 1

                while beg < len(content):
                    try:
                        print(f'Trying to send packet {packet}')
                        server_sock.sendto(self.create_packet('POST', packet, content[beg: beg + MAX_LINE // 2]), address)
                        received = server_sock.recv(MAX_LINE)
                        rcvd_method, rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if rcvd_packet == packet and 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {packet}')
                            beg += MAX_LINE // 2
                            packet = 1 - packet
                    except socket.timeout:
                        print('Timeout occurred')
                    except RuntimeError:
                        print('Checksum is not correct')

                while True:
                    try:
                        print(f'Trying to send END packet {packet}')
                        server_sock.sendto(self.create_packet('POST', packet, filename_.split('/')[-1], flags=['END']), address)
                        received = server_sock.recv(MAX_LINE)
                        rcvd_method, rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if rcvd_packet == packet and 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {packet}')
                            packet = 1 - packet
                            break
                    except socket.timeout:
                        print('Timeout occurred')
                    except RuntimeError:
                        print('Checksum is not correct')

            print(f'Successfully sent file {filename_}')

        except Exception as e:
            print(f'An error occurred: {e}')

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[3])

    server = Server(host, port, timeout)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
