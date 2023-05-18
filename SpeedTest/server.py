import socket
import time
import numpy as np
import tkinter as tk
from tkinter import ttk

PACKET_SIZE = 2048


class Server:
    def __init__(self, host_, port_, timeout_, protocol_):
        self._host    = host_
        self._port    = port_
        self._timeout = timeout_
        self._protocol = protocol_

    def receive_packets(self):
        if self._protocol == 'TCP':
            server_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
        elif self._protocol == 'UDP':
            server_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
        else:
            print('Protocol not supported!')
            return

        try:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self._host, self._port))
            server_sock.setblocking(False)
            server_sock.settimeout(self._timeout)
            conn = None
            if self._protocol == 'TCP':
                server_sock.listen()
                conn, _ = server_sock.accept()
                message = conn.recv(PACKET_SIZE)
            elif self._protocol == 'UDP':
                message, _ = server_sock.recvfrom(PACKET_SIZE)
            else:
                print('Protocol not supported!')
                return
            packets_num_ = int(message.decode('utf-8'))
            deltas = []

            while True:
                try:
                    if self._protocol == 'TCP':
                        message = conn.recv(PACKET_SIZE)
                    elif self._protocol == 'UDP':
                        message, _ = server_sock.recvfrom(PACKET_SIZE)
                    else:
                        print('Protocol not supported!')
                        return
                    recv_time = time.time()
                    message = message.decode('utf-8')
                    send_time = float(message.split('\r\n')[0])
                    deltas.append(1000 * (recv_time - send_time))
                    if len(deltas) == packets_num_:
                        break
                except BlockingIOError:
                    pass
                except socket.timeout:
                    break
            average_speed_ = np.mean(PACKET_SIZE / np.array(deltas))
            average_speed.set(f'{average_speed_:>.3f} KB/s')
            packets_num.set(f'{len(deltas)} of {packets_num_}')

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            server_sock.close()


def receive_clicked():
    root.title(f'{protocol.get()} server')
    server = Server(host_entry.get(), int(port_entry.get()), int(timeout_entry.get()), protocol.get())
    server.receive_packets()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('400x200+50+50')
    root.title('Server')
    root.resizable(False, False)

    choices = ['', 'TCP', 'UDP']
    protocol = tk.StringVar()
    protocol_menu = ttk.OptionMenu(root, protocol, *choices)
    protocol_menu.place(x=100, y=10)
    protocol_label = ttk.Label(root, text='Protocol:')
    protocol_label.place(x=10, y=10)

    host = tk.StringVar()
    host_entry = ttk.Entry(root, textvariable=host)
    host_entry.place(x=200, y=35, width=190)
    host_label = ttk.Label(root, text='Host:')
    host_label.place(x=10,  y=35)

    port = tk.StringVar()
    port_entry = ttk.Entry(root, textvariable=port)
    port_entry.place(x=200, y=60, width=190)
    port_label = ttk.Label(root, text='Port:')
    port_label.place(x=10, y=60)

    timeout = tk.StringVar()
    timeout_entry = ttk.Entry(root, textvariable=timeout)
    timeout_entry.place(x=200, y=85, width=190)
    timeout_label = ttk.Label(root, text='Timeout:')
    timeout_label.place(x=10, y=85)

    average_speed = tk.StringVar()
    average_speed_entry = ttk.Entry(root, textvariable=average_speed)
    average_speed_entry.place(x=200, y=110, width=190)
    average_speed_label = ttk.Label(root, text='Average speed:')
    average_speed_label.place(x=10, y=110)

    packets_num = tk.StringVar()
    packets_num_entry = ttk.Entry(root, textvariable=packets_num)
    packets_num_entry.place(x=200, y=135, width=190)
    packets_num_label = ttk.Label(root, text='Received packets:')
    packets_num_label.place(x=10, y=135)

    ttk.Button(root, text='Receive', command=receive_clicked).place(x=100, y=160, height=25, width=200)

    root.mainloop()