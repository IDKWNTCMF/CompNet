import socket
import sys
import pygame

MAX_LINE = 2048


class Server:
    def __init__(self, host_, port_):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host_, port_))
        self._socket.settimeout(1)

        self._shutdown = False
        pygame.init()
        self._window = pygame.display.set_mode((600, 400))
        pygame.display.set_caption('Server')
        self._window.fill((255, 255, 255))
        pygame.display.update()

    def serve_forever(self):
        while not self._shutdown:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._shutdown = True
                    break
            try:
                data, addr = self._socket.recvfrom(MAX_LINE)
            except socket.timeout:
                continue
            action = data.decode('utf-8').split()
            command = action[0]
            if command == 'point':
                coords = (int(action[1]), int(action[2]))
                pygame.draw.circle(self._window, (0, 0, 0), coords, 1)
            if command == 'line':
                coords = ((int(action[1]), int(action[2])), (int(action[3]), int(action[4])))
                pygame.draw.line(self._window, (0, 0, 0), coords[0], coords[1], 2)
            if command == 'quit':
                self._shutdown = True
            pygame.display.update()
        pygame.quit()


if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    server = Server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass