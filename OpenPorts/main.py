import socket
import sys
from contextlib import closing

def check_port(host_, port_):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(2)
        return sock.connect_ex((host_, port_)) == 0

if __name__ == '__main__':
    host = sys.argv[1]
    port_beg = int(sys.argv[2])
    port_end = int(sys.argv[3])

    open_ports = []
    for port in range(port_beg, port_end + 1):
        if check_port(host, port):
            open_ports.append(port)

    if len(open_ports) == 0:
        print('All ports among selected are busy')
    else:
        print('Open ports:')
        for port in open_ports:
            print(port)