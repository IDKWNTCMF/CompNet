import random
import sys
import socket

MAX_LINE = 2048
WINDOW_SIZE = 3


class Client:
    def __init__(self, server_host_, server_port_, client_host_, client_port_):
        self._server_host = server_host_
        self._server_port = server_port_
        self._client_host = client_host_
        self._client_port = client_port_

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

    def send_file(self, filename_):
        try:
            with open(filename_, 'r') as f:
                content = f.read()

            client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_sock.bind((self._client_host, self._client_port))
            client_sock.settimeout(1)

            expected = 0
            max_packet = (len(content) - 1) // (MAX_LINE // 2) + 1
            window = (1, min(max_packet, WINDOW_SIZE))

            while True:
                try:
                    print(f'Send BEG packet 0')
                    client_sock.sendto(self.create_packet(0, filename_.split('/')[-1], flags=['BEG']), (self._server_host, self._server_port))
                    received = client_sock.recv(MAX_LINE)
                    rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                    if rcvd_packet == 0 and 'ACK' in rcvd_flags:
                        print(f'ACK received for BEG packet 0')
                        expected += 1
                        break

                except socket.timeout:
                    print('Timeout occurred!')

            print(f'Initial window: {window[0]} : {window[1]}')
            while (window[0] - 1) * MAX_LINE // 2 < len(content):
                packet = window[0]
                while packet <= window[1] and (packet - 1) * MAX_LINE // 2 < len(content):
                    try:
                        if random.randint(0, 9) >= 2:
                            print(f'Send packet {packet}')
                            client_sock.sendto(self.create_packet(packet, content[(packet - 1) * MAX_LINE // 2 : packet * MAX_LINE // 2]), (self._server_host, self._server_port))
                        else:
                            print(f'Packet {packet} lost')
                        packet += 1

                    except BlockingIOError:
                        pass

                while True:
                    try:
                        received = client_sock.recv(MAX_LINE)
                        rcvd_packet, rcvd_flags, rcvd_content = self.parse_message(received)
                        if 'ACK' in rcvd_flags:
                            print(f'ACK received for packet {rcvd_packet}')
                            last_sent = window[1]
                            window = (rcvd_packet + 1, min(max_packet, rcvd_packet + WINDOW_SIZE))
                            if window[0] <= window[1]:
                                print(f'New window: {window[0]} : {window[1]}')
                            for packet in range(last_sent + 1, window[1]):
                                if random.randint(0, 9) >= 2:
                                    print(f'Send packet {packet}')
                                    client_sock.sendto(self.create_packet(packet, content[(packet - 1) * MAX_LINE // 2 : packet * MAX_LINE // 2]), (self._server_host, self._server_port))
                                else:
                                    print(f'Packet {packet} lost')
                            if rcvd_packet == max_packet:
                                break
                    except socket.timeout:
                        print('Timeout occurred!')
                        break

            print(f'Successfully sent file {filename_}')

        except Exception as e:
            print(f'An error occurred: {e}')


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    client_host = sys.argv[3]
    client_port = int(sys.argv[4])
    filename = sys.argv[5]

    client = Client(server_host, server_port, client_host, client_port)
    try:
        client.send_file(filename)
    except KeyboardInterrupt:
        pass