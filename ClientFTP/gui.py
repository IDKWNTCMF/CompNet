import tkinter as tk
from tkinter import ttk
from ftplib import FTP, all_errors
from window import Window

root = tk.Tk()
root.geometry('400x400+50+50')
root.title('FTP Client')

root.resizable(False, False)

ftp = FTP()


def button_clicked():
    print('Button clicked')


username = tk.StringVar()
username_entry = ttk.Entry(root, textvariable=username)
username_entry.place(x=5, y=10, width=190)

password = tk.StringVar()
password_entry = ttk.Entry(root, textvariable=password, show='*')
password_entry.place(x=5, y=35, width=190)

host_port = tk.StringVar()
host_port_entry = ttk.Entry(root, textvariable=host_port)
host_port_entry.place(x=205, y=10, width=190)

output_text = tk.Text(root)
output_text.place(x=5, y=70, height=200, width=390)

filename = tk.StringVar()
filename_entry = ttk.Entry(root, textvariable=filename, width=30)
filename_entry.place(x=10, y=280)


def get_files(dir=None):
    output_text.delete('1.0', 'end')
    files = ftp.nlst() if dir is None else ftp.nlst(dir)
    for idx, file in enumerate(files):
        output_text.insert(f'{idx + 1}.0', f'{file}\n')


def connect_clicked():
    if ':' in host_port_entry.get() and len(username_entry.get()) != 0:
        host = host_port_entry.get().split(':')[0]
        port = int(host_port_entry.get().split(':')[1])
        ftp.connect(host, port)
        ftp.login(username_entry.get(), password_entry.get())
        print(f'Successfully connected to {host_port_entry.get()}')
        get_files()


def create_clicked():
    def window_saved(event):
        text = window.output_text.get('1.0', 'end-1c')
        with open(filename_entry.get(), 'w') as file:
            file.write(text)
        with open(filename_entry.get(), 'rb') as file:
            ftp.storlines(f'STOR {filename_entry.get()}', file)
        print(f'{filename_entry.get()} saved successfully')
        get_files()

    try:
        window = Window(root)
        window.grab_set()
        window.bind('<Control-KeyPress-s>', window_saved)
    except all_errors as e:
        print(f'An error occurred while creating file: {e}')


def retrieve_clicked():
    try:
        output_text.delete('1.0', 'end')
        response = ftp.retrlines(f'RETR {filename_entry.get()}', lambda line: output_text.insert('end', f'{line}\n'))

        if response.startswith('226'):
            print(f'File {filename_entry.get()} retrieved successfully')
        else:
            print(f'Error occurred while retrieving. Local file may be corrupt')
    except all_errors as e:
        print(f'An error occurred while retrieving file: {e}')


def update_clicked():
    def window_saved(event):
        text = window.output_text.get('1.0', 'end-1c')
        with open(filename_entry.get(), 'w') as file:
            file.write(text)
        with open(filename_entry.get(), 'rb') as file:
            ftp.storlines(f'STOR {filename_entry.get()}', file)
        print(f'{filename_entry.get()} saved successfully')
        get_files()

    try:
        with open(filename_entry.get(), 'w') as file:
            response = ftp.retrlines(f'RETR {filename_entry.get()}', file.write)

            if response.startswith('226'):
                print(f'File {filename_entry.get()} retrieved successfully')
            else:
                print(f'Error occurred while updating. Local file may be corrupt')
        window = Window(root, open(filename_entry.get(), 'r').read())
        window.grab_set()
        window.bind('<Control-KeyPress-s>', window_saved)
    except all_errors as e:
        print(f'An error occurred while updating file: {e}')


def delete_clicked():
    try:
        ftp.delete(filename_entry.get())
        print(f'File {filename_entry.get()} deleted successfully')
        get_files()
    except all_errors as e:
        print(f'An error occurred while deleting file: {e}')


ttk.Button(root, text='Connect',  command=connect_clicked).place(x=205, y=35, height=25, width=190)

ttk.Button(root, text='Create',   command=create_clicked).place(x=300, y=280, width=95)
ttk.Button(root, text='Retrieve', command=retrieve_clicked).place(x=300, y=310, width=95)
ttk.Button(root, text='Update',   command=update_clicked).place(x=300, y=340, width=95)
ttk.Button(root, text='Delete',   command=delete_clicked).place(x=300, y=370, width=95)

root.mainloop()
