import socket
import sys

args = sys.argv

class BasicServer(object):
    
    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.bind(("", int(port)))
        self.socket.listen(5)
    
    def start(self):
        while True:
            (new_socket, address) = self.socket.accept()
            msg = new_socket.recv(1024)
            tmp = msg
            while tmp:
                tmp = new_socket.recv(1024)
                msg += tmp
            print msg
    

if len(args) != 2:
    print "Please supply a port."
    sys.exit()
server = BasicServer(args[1])
server.start()
