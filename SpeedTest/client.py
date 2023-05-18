import random
import socket
import string
import time
import tkinter as tk
from tkinter import ttk


PACKET_SIZE = 2048

def generate_message(sz):
    return ''.join([random.choice(string.ascii_letters) for _ in range(sz)])

class Client:
    def __init__(self, host_, port_, protocol_):
        self._host = host_
        self._port = port_
        self._protocol = protocol_

    def send_packets(self, packets_num_):
        if self._protocol == 'TCP':
            client_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )
        elif self._protocol == 'UDP':
            client_sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
        else:
            print('Protocol not supported!')
            return

        try:
            if self._protocol == 'TCP':
                client_sock.connect((self._host, self._port))
                client_sock.send(str(packets_num_).encode('utf-8'))
            elif self._protocol == 'UDP':
                client_sock.sendto(str(packets_num_).encode('utf-8'), (self._host, self._port))
            else:
                print('Protocol not supported!')
                return

            for _ in range(packets_num_):
                send_time = str(time.time())
                message = send_time + '\r\n' + generate_message(PACKET_SIZE - len(send_time) - len('\r\n'))
                if self._protocol == 'TCP':
                    client_sock.send(message.encode('utf-8'))
                elif self._protocol == 'UDP':
                    client_sock.sendto(message.encode('utf-8'), (self._host, self._port))
                else:
                    print('Protocol not supported!')
                    return
        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            client_sock.close()


def send_clicked():
    root.title(f'{protocol.get()} client')
    client = Client(host_entry.get(), int(port_entry.get()), protocol.get())
    client.send_packets(int(packets_num.get()))


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('400x150+50+300')
    root.title('Client')
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
    host_label.place(x=10, y=35)

    port = tk.StringVar()
    port_entry = ttk.Entry(root, textvariable=port)
    port_entry.place(x=200, y=60, width=190)
    port_label = ttk.Label(root, text='Port:')
    port_label.place(x=10, y=60)

    packets_num = tk.StringVar()
    packets_num_entry = ttk.Entry(root, textvariable=packets_num)
    packets_num_entry.place(x=200, y=85, width=190)
    packets_num_label = ttk.Label(root, text='Number of packets to send:')
    packets_num_label.place(x=10, y=85)

    ttk.Button(root, text='Send', command=send_clicked).place(x=100, y=110, height=25, width=200)

    root.mainloop()