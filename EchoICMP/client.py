import struct
import sys
import socket
import time
import datetime

import numpy as np

ICMP_ECHO = 8
MAX_LINE = 2048
PACKETS = 5

ICMP_TYPE_CODE_TO_ERROR = {
    (3, 0): 'Network unreachable',
    (3, 1): 'Host unreachable',
    (3, 2): 'Port unavailable',
    (3, 4): 'Message fragmentation required',
    (3, 5): 'Source route is out of order',
    (3, 6): 'Destination network unknown',
    (3, 7): 'Destination host unknown',
    (3, 8): 'Host isolated',
    (3, 9): 'Communication with the destination network is administratively prohibited',
    (3, 10): 'Communication with the destination host is administratively prohibited',
    (3, 11): 'The network is not available for this type of service',
    (3, 12): 'The host is not available for this type of service',
    (3, 13): 'Communication is administratively prohibited by a filter',
    (3, 14): 'Hosts seniority violation',
    (3, 15): 'Seniority discrimination',
    (4, 0): 'The source was disabled: queue is full',
    (11, 0): 'Time limit exceeded when transferring',
    (11, 1): 'Time limit exceeded during assembly',
    (12, 0): 'Incorrect IP header',
    (12, 1): 'Required option missing'
}


class Client:
    def __init__(self, host_, timeout_):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        self._socket.settimeout(timeout_)

        self._host = host_
        self._rtts = []

    def calculate_checksum(self, data):
        step = 2
        checksum = 0
        for i in range(0, len(data), step):
            if i + 1 < len(data):
                checksum += (data[i + 1] << 8) + data[i]
            else:
                checksum += data[i]

        checksum %= 2 ** 32
        checksum = (checksum & 0xffff) + (checksum >> 16)
        checksum %= 2 ** 16
        return socket.htons(0xffff - checksum)

    def validate_checksum(self, data):
        step = 2
        checksum = 0
        for i in range(0, len(data), step):
            if i + 1 < len(data):
                checksum += (data[i + 1] << 8) + data[i]
            else:
                checksum += data[i]

        checksum %= 2 ** 32
        checksum = (checksum & 0xffff) + (checksum >> 16)
        checksum %= 2 ** 16
        return checksum == 0xffff

    def send_one_ping(self):
        checksum_ = 0
        header = struct.pack('!BBHHH', ICMP_ECHO, 0, checksum_, 1, 1)
        data = str(datetime.datetime.now()).encode('utf-8')
        checksum_ = self.calculate_checksum(header + data)

        header = struct.pack('!BBHHH', ICMP_ECHO, 0, checksum_, 1, 1)
        packet = header + data
        send_time = time.time()

        try:
            while packet:
                new_beg = self._socket.sendto(packet, (self._host, 1))
                packet = packet[new_beg : ]
        except socket.error:
            print(f'An error occurred while trying to ping {self._host}!')
            self._socket.close()
            return

        return send_time

    def receive_one_ping(self):
        while True:
            try:
                packet_data, addr = self._socket.recvfrom(MAX_LINE)
                receive_time = time.time()
                icmp_data = packet_data[20 :]
                if not self.validate_checksum(icmp_data):
                    print('Checksum is incorrect!')
                    return None

                header = icmp_data[: 8]
                packet_type, code, checksum, p_id, seq_number = struct.unpack('!BBHHH', header)
                if 1 == p_id:
                    if (packet_type, code) in ICMP_TYPE_CODE_TO_ERROR:
                        print(ICMP_TYPE_CODE_TO_ERROR[(packet_type, code)])
                        return None
                    return receive_time
            except socket.timeout:
                print('Timeout occurred while waiting for response of ping!')
                return None

    def print_stats(self, rtt):
        self._rtts.append(rtt)
        print(f'icmp_seq: {len(self._rtts)}, RTT CUR/MIN/AVG/MAX = {self._rtts[-1]:.3f}/{np.min(self._rtts):.3f}/{np.mean(self._rtts):.3f}/{np.max(self._rtts):.3f} ms')

    def print_final_stats(self):
        print('--- ping statistics ---')
        print(f'{PACKETS} packets transmitted, {len(self._rtts)} received, {100 * (1 - len(self._rtts) / PACKETS):.3f}% packet loss')
        print(f'RTT MIN/AVG/MAX = {np.min(self._rtts):.3f}/{np.mean(self._rtts):.3f}/{np.max(self._rtts):.3f} ms')


if __name__ == '__main__':
    host = sys.argv[1]
    delay = 1
    timeout = 1
    client = Client(host, timeout)

    for packet_num in range(PACKETS):
        snd_time = client.send_one_ping()
        rcv_time = client.receive_one_ping()
        if rcv_time is not None:
            client.print_stats(1000 * (rcv_time - snd_time))
        else:
            print('Packet lost')
        time.sleep(1)

    client.print_final_stats()