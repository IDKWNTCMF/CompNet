import socket
import sys


def send_query(host, port, filename):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_sock.connect((host, port))

    client_sock.sendall(f'GET /{filename} HTTP/1.1\r\nHost: {host}:{port}'.encode('iso-8859-1'))
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
