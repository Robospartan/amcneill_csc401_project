import os
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((str(os.getenv('hostname')), 7734))

s.listen(5)

while True:
    connection_socket, addr = s.accept()
    print('Connected to ', addr)
    msg = connection_socket.recv(256)
    print(str(msg, 'utf-8'))
    connection_socket.close()