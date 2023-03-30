import sys
import socket
import subprocess

MAX_LINE = 2048
class Server:
    def __init__(self, host_, port_):
        self._host = host_
        self._port = port_

    def serve_forever(self):
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.listen()

            while True:
                client_sock, _ = server_sock.accept()
                self.serve_client(client_sock)

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            server_sock.close()

    def serve_client(self, client_sock):
        try:
            print('----------------------------BEGIN REMOTE EXECUTION--------------------------------------')
            command = client_sock.recv(MAX_LINE).decode()
            print(command)
            executor = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            for stdout in executor.stdout:
                print(stdout.decode(), flush=True, end='')
                client_sock.sendall(stdout)
            for stderr in executor.stderr:
                print(stderr.decode(), flush=True, end='')
                client_sock.sendall(stderr)
            print('----------------------------END   REMOTE EXECUTION--------------------------------------')
        except BrokenPipeError:
            print(f'Remote execution failed while handling: {command}')
            print('----------------------------END   REMOTE EXECUTION--------------------------------------')

        if client_sock:
            client_sock.close()


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])

    server = Server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass