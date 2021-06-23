import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((sys.argv[1], 7734))

s.send(bytes(sys.argv[2], 'utf-8'))

s.close()