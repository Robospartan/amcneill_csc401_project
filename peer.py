import os
from pathlib import Path
import platform
import socket
import sys
import threading
import time

rfc_dir = Path(sys.argv[3])
upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
upload_socket.bind((sys.argv[2], 0))
upload_port = upload_socket.getsockname()[1]

def rfc_upload():
    upload_socket.listen(5)
    while True:
        upload_connection = upload_socket.accept()[0]
        try:
            raw_request = str(upload_connection.recv(4096), 'utf-8')
            request = raw_request.split()
            rfc_number = 'RFC ' + request[2]
            response = ''
            if request[3] != 'P2P-CI/1.0':
                response = 'P2P-CI/1.0 505 P2P-CI Version Not Supported\nDate: ' + time.strftime('%a, %d %b %Y %X %Z', time.gmtime(time.time())) + '\nOS: ' + platform.platform() + '\n'
            else:
                for rfc in rfc_dir.iterdir():
                    if rfc.name.startswith(rfc_number):
                        response += 'P2P-CI/1.0 200 OK\nDate: ' + time.strftime('%a, %d %b %Y %X %Z', time.gmtime(time.time())) + '\n'
                        response += 'OS: ' + platform.platform() + '\nLast-Modified: ' + time.strftime('%a, %d %b %Y %X %Z', time.gmtime(os.stat(rfc.absolute()).st_mtime)) + '\n'
                        response += 'Content-Length: ' + str(os.stat(rfc.absolute()).st_size) + '\nContent-Type: text/plain\n'
                        with rfc.open() as f:
                            response += f.read()
                if response == '':
                    response += 'P2P-CI/1.0 404 Not Found\nDate: ' + time.strftime('%a, %d %b %Y %X %Z', time.gmtime(time.time())) + '\nOS: ' + platform.platform() + '\n'
            upload_connection.send(bytes(response, 'utf-8'))
        except:
            response = 'P2P-CI/1.0 400 Bad Request\nDate: ' + time.strftime('%a, %d %b %Y %X %Z', time.gmtime(time.time())) + '\nOS: ' + platform.platform() + '\n'
            upload_connection.send(bytes(response, 'utf-8'))
        upload_connection.close()

upload_thread = threading.Thread(target=rfc_upload)
upload_thread.start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((sys.argv[1], 7734))

for rfc in rfc_dir.iterdir():
    name = rfc.name
    end_of_rfc_number = name.find(' ', 4)
    request = 'ADD ' + name[: end_of_rfc_number] + ' P2P-CI/1.0\nHost: ' + sys.argv[2] + '\nPort: ' + str(upload_port) + '\nTitle: ' + name[end_of_rfc_number + 1 :]
    s.send(bytes(request, 'utf-8'))
    response = str(s.recv(4096), 'utf-8')
    print(response)

print('Command format: (ADD/LOOKUP/LIST/CLOSE) (RFC_Number) (RFC_Title) (GET optional)')
while True:
    try:
        command = input('Enter a Command: ').split()
        if command[0] == 'CLOSE':
            s.send(bytes('CLOSE ' + sys.argv[2] + '\n', 'utf-8'))
            s.close()
            os._exit(0)
        else:
            request = ''
            if command[0] == 'LIST':
                request = 'LIST ALL P2P-CI/1.0\nHost: ' + sys.argv[2] + '\nPort: ' + str(upload_port) + '\n'
            else:
                request = command[0] + ' RFC ' + command[1] + ' P2P-CI/1.0\nHost: ' + sys.argv[2] + '\nPort: ' + str(upload_port) + '\nTitle:'
                for segment_index in range(2, len(command)):
                    request += ' ' + command[segment_index]
                request += '\n'
            s.send(bytes(request, 'utf-8'))
            response = str(s.recv(4096), 'utf-8')
            print(response)
            if command[0] == 'LOOKUP' and command[len(command)-1] == 'GET':
                response_lines = response.splitlines()
                if response_lines[0] == 'P2P-CI/1.0 200 OK':
                    rfc_info = response_lines[1].split()
                    download_rfc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    download_rfc_sock.connect((rfc_info[len(rfc_info)-2], int(rfc_info[len(rfc_info)-1])))
                    download_rfc_sock.send(bytes('GET RFC ' + rfc_info[1] + ' P2P-CI/1.0\nHost: ' + rfc_info[len(rfc_info)-2] + '\nOS: ' + platform.platform() + '\n', 'utf-8'))
                    peer_response = str(download_rfc_sock.recv(4096), 'utf-8')
                    print(peer_response)
                    if peer_response.split()[1] == '200':
                        data_start = peer_response.find('Content-Type: text/plain\n') + len('Content-Type: text/plain\n')
                        rfc_name = sys.argv[3] + '/RFC ' + command[1]
                        for segment_index in range(2, len(command)-1):
                            rfc_name += ' ' + command[segment_index]
                        new_rfc = open(rfc_name, 'w')
                        new_rfc.write(peer_response[data_start :])
                        new_rfc.close()
    except:
        print('Invalid command.')
        print('Command format: (ADD/LOOKUP/LIST/CLOSE) (RFC_Number) (RFC_Title) (GET optional)')