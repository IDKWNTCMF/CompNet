import sys
import pygame
import socket


class Client:
    def __init__(self, server_host_, server_port_):
        self._server_host = server_host_
        self._server_port = server_port_
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._shutdown = False
        pygame.init()
        self._window = pygame.display.set_mode((600, 400))
        pygame.display.set_caption('Client')
        self._window.fill((255, 255, 255))
        pygame.display.update()

    def run(self):
        last_point = None
        while not self._shutdown:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    coords = pygame.mouse.get_pos()
                    pygame.draw.circle(self._window, (0, 0, 0), coords, 1)
                    self._socket.sendto(f'point {coords[0]} {coords[1]}'.encode('utf-8'), (self._server_host, server_port))
                    last_point = coords

                if event.type == pygame.MOUSEBUTTONUP:
                    last_point = None

                if last_point is not None and event.type == pygame.MOUSEMOTION:
                    coords = pygame.mouse.get_pos()
                    pygame.draw.line(self._window, (0, 0, 0), last_point, coords, 2)
                    action = f'line {last_point[0]} {last_point[1]} {coords[0]} {coords[1]}'
                    self._socket.sendto(action.encode('utf-8'), (self._server_host, server_port))
                    last_point = coords

                if event.type == pygame.QUIT:
                    self._shutdown = True
                    self._socket.sendto('quit'.encode('utf-8'), (self._server_host, server_port))
                    break
            pygame.display.update()
        pygame.quit()


if __name__ == '__main__':
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    client = Client(server_host, server_port)
    try:
        client.run()
    except KeyboardInterrupt:
        pass