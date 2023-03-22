import os
import socket
import sys
import threading
from queue import Queue
from request import Request
from response import Response

MAX_LINE = 10**5

class Server:
    def __init__(self, host_, port_, concurrency_level_):
        self._host = host_
        self._port = port_
        self._concurrency_level = concurrency_level_
        self._queue = Queue()

    def serve_forever(self):
        server_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0
        )

        try:
            server_sock.bind((self._host, self._port))
            server_sock.listen(concurrency_level)
            server_sock.setblocking(False)

            while True:
                try:
                    client_sock, _ = server_sock.accept()
                    self._queue.put(client_sock)
                except BlockingIOError:
                    pass
                if not self._queue.empty():
                    try:
                        if threading.active_count() < concurrency_level:
                            client_sock = self._queue.get()
                            thr = threading.Thread(target=self.serve_client, args=(client_sock,))
                            thr.start()
                        elif concurrency_level == 1:
                            client_sock = self._queue.get()
                            self.serve_client(client_sock)
                    except Exception as e:
                        print('Client serving failed', e)

        finally:
            server_sock.close()

    def serve_client(self, client_sock):
        try:
            req = self.parse_request(client_sock)
            resp = self.handle_request(req)
            self.send_response(client_sock, resp)
        except ConnectionResetError:
            client_sock = None
        except Exception as e:
            self.send_error(client_sock, e)

        if client_sock:
            client_sock.close()

    def parse_request(self, client_sock):
        rfile = client_sock.makefile('rb')
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise Exception('Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        req_line = req_line.rstrip('\r\n')
        words = req_line.split()
        if len(words) != 3:
            raise Exception('Malformed request line')

        method, target, _ = words

        return Request(method, target)

    def handle_request(self, req):
        path = req.path[1:]
        content_type = 'text/plain; charset=utf-8'
        if os.path.exists(path):
            file = open(path, mode='rb')
            response = file.read()
            file.close()
            status = 200
            reason = 'OK'
            headers = [('Content-Type', content_type), ('Content-Length', len(response))]
            return Response(status, reason, headers, response)
        else:
            status = 404
            reason = 'Not Found'
            response = b'404 Not Found'
            headers = [('Content-Length', len(response))]
            return Response(status, reason, headers, response)

    def send_response(self, client_sock, resp):
        wfile = client_sock.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body)

        wfile.flush()
        wfile.close()

    def send_error(self, client_sock, err):
        try:
            status = err.status
            reason = err.reason
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = 500
            reason = 'Internal Server Error'
            body = b'500 Internal Server Error'
        resp = Response(status, reason, [('Content-Length', len(body))], body)
        self.send_response(client_sock, resp)



if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    concurrency_level = int(sys.argv[3])

    serv = Server(host, port, concurrency_level)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
