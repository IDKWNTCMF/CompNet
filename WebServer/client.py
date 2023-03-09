import socket
import sys


def send_query(host_, port_, filename_):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_sock.connect((host_, port_))

    client_sock.sendall(f'GET /{filename_} HTTP/1.1\r\nHost: {host_}:{port_}'.encode('iso-8859-1'))
    client_sock.shutdown(socket.SHUT_WR)

    responses = []
    while True:
        data = client_sock.recv(2048)
        if not data:
            break
        responses.append(data)
    print((b''.join(responses)).decode())

    client_sock.close()

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    send_query(host, port, filename)
