import socket
import struct
import sys
import time

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
    def __init__(self, timeout_, number_of_pings_):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        self._socket.settimeout(timeout_)

        self._number_of_pings = number_of_pings_

    def calculate_checksum(self, data):
        step = 2
        checksum = 0
        for i in range(0, len(data), step):
            if i + 1 < len(data):
                checksum += (data[i] << 8) + data[i + 1]
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
                checksum += (data[i] << 8) + data[i + 1]
            else:
                checksum += data[i]

        checksum %= 2 ** 32
        checksum = (checksum & 0xffff) + (checksum >> 16)
        checksum %= 2 ** 16
        return checksum == 0xffff

    def ping_with_ttl(self, host_, time_to_live):
        print(time_to_live, end=' ')
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, time_to_live)
        addr = None
        for _ in range(self._number_of_pings):
            try:
                checksum = 0
                header = struct.pack('!BBHHH', ICMP_ECHO, 0, checksum, time_to_live, 1)
                checksum = self.calculate_checksum(header)
                header = struct.pack('!BBHHH', ICMP_ECHO, 0, checksum, time_to_live, 1)
                self._socket.sendto(header, (host_, 1))
                send_time = time.time()

                packet_data, cur_addr = self._socket.recvfrom(MAX_LINE)
                receive_time = time.time()
                if packet_data is not None:
                    icmp_data = packet_data[20 :]
                    if not self.validate_checksum(icmp_data):
                        print('Checksum is incorrect!')
                        continue

                    header = icmp_data[: 8]
                    packet_type, code, checksum, p_id, seq_number = struct.unpack('!BBHHH', header)
                    if time_to_live == p_id:
                        if (packet_type, code) in ICMP_TYPE_CODE_TO_ERROR:
                            print(ICMP_TYPE_CODE_TO_ERROR[(packet_type, code)])
                            continue

                    if cur_addr is not None:
                        if addr is None:
                            print(f'{cur_addr[0]}', end=' ')
                            addr = cur_addr
                        print(f'{1000 * (receive_time - send_time):.3f} ms', end=' ')

            except socket.timeout:
                print('*', end=' ')
                continue

        addr_ = socket.gethostbyname(host_)
        if addr is not None:
            hostname = 'Unknown host'
            try:
                hostname = socket.gethostbyaddr(addr[0])[0]
            except Exception:
                pass
            finally:
                print(f'| {hostname}')
        else:
            print()
        return addr is not None and addr[0] == addr_

    def trace(self, host_):
        print(f'traceroute to {host_}, 64 hops max')
        time_to_live = 1
        while time_to_live <= 64:
            if self.ping_with_ttl(host_, time_to_live):
                break
            time_to_live += 1


if __name__ == '__main__':
    host = sys.argv[1]
    number_of_pings = int(sys.argv[2])
    timeout = 1
    client = Client(timeout, number_of_pings)

    try:
        client.trace(host)
    except KeyboardInterrupt:
        pass