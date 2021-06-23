import socket
import sys
import threading

class Peer:
    def __init__(self, hostname, port):
        self.hostname: str = hostname
        self.port: int = port
        self.next_peer: Peer = None

class RFC:
    def __init__(self, rfc_number, rfc_title, rfc_peer_hostname):
        self.rfc_number: int = rfc_number
        self.rfc_title: str = rfc_title
        self.rfc_peer_hostname: str = rfc_peer_hostname
        self.next_rfc: RFC = None

peer_head = Peer()
rfc_head = RFC()

modifying_peer_list = threading.Semaphore(1)
modifying_rfc_list = threading.Semaphore(1)

def peer_connection(socket: socket.socket, addr):
    first_add = True
    while True:
        request_lines = str(socket.recv(1024), "utf-8").splitlines()
        request = {}
        try:
            request_first_line = request_lines[0].split()
            request = {
                'method': request_first_line[0],
                'rfc_number': request_first_line[2],
                'version': request_first_line[len(request_first_line) - 1]
            }
            for line_index in range(1, len(request_lines)):
                line = request_lines[line_index]
                header_field_start = line.find(':')
                request[line[: header_field_start]] = line[header_field_start + 2 :]
        except IndexError:
            socket.send('P2P-CI/1.0 400 Bad Request\r\n')
        try:
            if request['version'] != 'P2P-CI/1.0':
                socket.send('P2P-CI/1.0 505 P2P-CI Version not Supported\r\n')
            elif request['method'] == 'ADD':
                if first_add:
                    modifying_peer_list.acquire()
                    curr_peer = peer_head
                    while curr_peer.next_peer != None:
                        curr_peer = curr_peer.next_peer
                    curr_peer.next_peer = Peer(request['Host'], request['Port'])
                    modifying_peer_list.release()
                    first_add = False
                modifying_rfc_list.acquire()
                curr_rfc = rfc_head
                while curr_rfc.next_rfc != None:
                    curr_rfc = curr_rfc.next_rfc
                curr_rfc.next_rfc = RFC(request['rfc_number'], request['Title'], request['Host'])
                modifying_rfc_list.release()
                socket.send(request['version'] + ' 200 OK\r\nRFC ' + request['rfc_number'] + ' ' + request['Title'] + ' ' + request['Host'] + ' ' + request['Port'] + '\r\n')
            elif request['method'] == 'LOOKUP':
                curr_rfc = rfc_head.next_rfc
                rfc_list = ''
                while curr_rfc != None:
                    if curr_rfc.rfc_title == request['Title']:
                        rfc_list += 'RFC ' + curr_rfc.rfc_number + ' ' + curr_rfc.rfc_title + ' ' + curr_rfc.rfc_peer_hostname
                        curr_peer = peer_head.next_peer
                        while curr_peer.hostname != curr_rfc.rfc_peer_hostname:
                            curr_peer = curr_peer.next_peer
                        rfc_list += ' ' + curr_peer.port + '\r\n'
                    curr_rfc = curr_rfc.next_rfc
                if rfc_list == '':
                    socket.send('P2P-CI/1.0 404 Not Found\r\n')
                else:
                    socket.send('P2P-CI/1.0 200 OK\r\n' + rfc_list)
            elif request['method'] == 'LIST':
                curr_rfc = rfc_head.next_rfc
                rfc_list = ''
                while curr_rfc != None:
                    rfc_list += 'RFC ' + curr_rfc.rfc_number + ' ' + curr_rfc.rfc_title + ' ' + curr_rfc.rfc_peer_hostname
                    curr_peer = peer_head.next_peer
                    while curr_peer.hostname != curr_rfc.rfc_peer_hostname:
                        curr_peer = curr_peer.next_peer
                    rfc_list += ' ' + curr_peer.port + '\r\n'
                socket.send('P2P-CI/1.0 200 OK\r\n' + rfc_list)
            else:
                socket.send('P2P-CI/1.0 400 Bad Request\r\n')
        except KeyError:
            socket.send('P2P-CI/1.0 400 Bad Request\r\n')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((sys.argv[1], 7734))

s.listen(5)

while True:
    threading.Thread(target=peer_connection, args=s.accept()).start()
