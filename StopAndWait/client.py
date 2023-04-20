import socket
import random
import sys
import os

from Checksum.checksum import get_checksum, val_checksum

MAX_LINE = 2048


class Client:
    def __init__(self, server_host_, server_port_, client_host_, client_port_, timeout_):
        self._server_host = server_host_
        self._server_port = server_port_
        self._timeout = timeout_
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_sock.bind((client_host_, client_port_))

        if not os.path.exists('client_files'):
            os.mkdir('client_files')

        if not os.path.exists('client_files/received'):
            os.mkdir('client_files/received')

    def send_file(self, filename_):
        try:
            with open(filename_, 'r') as f:
                content = f.read()
                self.client_sock.settimeout(self._timeout)
                beg = 0
                packet = 0

                while True:
                    try:
                        print(f'Trying to send BEG packet {packet}')
                        self.client_sock.sendto(self.create_packet('POST', packet, filename_.split('/')[-1], flags=['BEG']), (self._server_host, self._server_port))
                        received = self.client_sock.recv(MAX_LINE)
                        rcvd_method, rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if rcvd_packet == packet and 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {packet}')
                            packet = 1 - packet
                            break
                    except socket.timeout:
                        print('Timeout occurred')
                    except RuntimeError:
                        print('Checksum is not correct')

                while beg < len(content):
                    try:
                        print(f'Trying to send packet {packet}')
                        self.client_sock.sendto(self.create_packet('POST', packet, content[beg : beg + MAX_LINE // 2]), (self._server_host, self._server_port))
                        received = self.client_sock.recv(MAX_LINE)
                        rcvd_method, rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if rcvd_packet == packet and 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {packet}')
                            beg += MAX_LINE // 2
                            packet = 1 - packet
                    except socket.timeout:
                        print('Timeout occurred')
                    except RuntimeError:
                        print('Checksum is not correct')

            print(f'Successfully sent file {filename_}')

        except Exception as e:
            print(f'An error occurred: {e}')


    def get_file(self, filename_):
        try:
            new_filename_ = 'client_files/received/' + filename_.split('/')[-1]

            if os.path.exists(new_filename_):
                os.remove(new_filename_)

            with open(new_filename_, 'a') as f:
                packet = 0
                self.client_sock.settimeout(self._timeout)
                while True:
                    try:
                        print(f'Trying to send BEG packet {packet}')
                        self.client_sock.sendto(self.create_packet('GET', packet, filename_, flags=['BEG']), (self._server_host, self._server_port))
                        received = self.client_sock.recv(MAX_LINE)
                        rcvd_method, rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if rcvd_packet == packet and 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {packet}')
                            packet = 1 - packet
                            break
                    except socket.timeout:
                        print('Timeout occurred')
                    except RuntimeError:
                        print('Checksum is not correct')

                while True:
                    try:
                        message, address = self.client_sock.recvfrom(MAX_LINE)
                        method_, packet, flags, content = self.parse_message(message)
                        print(f'Received packet {packet}')

                        if random.randint(0, 9) >= 2:
                            self.client_sock.sendto(self.create_packet('', packet, '', flags=['ACK']), address)
                            print(f'ACK sent for packet {packet}')
                            if 'END' in flags:
                                break

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
        content = '\r\n'.join(message[3 :])[9 :]
        return method_, packet, flags, content


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    client_host = sys.argv[3]
    client_port = int(sys.argv[4])
    timeout = int(sys.argv[5])
    method = sys.argv[6]
    filename = sys.argv[7]

    client = Client(server_host, server_port, client_host, client_port, timeout)

    try:
        if method == 'upload':
            client.send_file(filename)
        if method == 'download':
            client.get_file(filename)
    except KeyboardInterrupt:
        pass
