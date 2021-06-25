import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((sys.argv[1], 7734))

# LIST request with invalid command
request = 'List ALL P2P-CI/1.0\nHost: ' + sys.argv[2] + '\nPort: 39054\n'
s.send(bytes(request, 'utf-8'))
response = str(s.recv(4096), 'utf-8')
print(response)


# LIST request with invalid version
request = 'LIST ALL P2P-CI/2.0\nHost: ' + sys.argv[2] + '\nPort: 39054\n'
s.send(bytes(request, 'utf-8'))
response = str(s.recv(4096), 'utf-8')
print(response)
