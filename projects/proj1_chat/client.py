import socket
import sys
import utils
import select

class Client(object):

    def __init__(self, name, address, port):
        self.address = address
        self.name = name
        self.port = int(port)
        self.socket = socket.socket()
        self.all_sockets = [self.socket, sys.stdin]
        try:
            self.socket.connect((self.address, self.port))
        except:
            print utils.CLIENT_CANNOT_CONNECT.format(address, port)
            
    def send(self, message):
        self.socket.send(message)

def padMessage(message):        
    original_message_length = len(message)
    return message.ljust(utils.MESSAGE_LENGTH - original_message_length + 1)

args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address and port."
    sys.exit() 

client = Client(args[1], args[2], args[3])
client.send(client.name)

sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
sys.stdout.flush()

try:     
    while True:
        read_sockets, _, error_sockets = select.select(client.all_sockets, [], [])
        for sock in read_sockets:
            if sock == client.socket:
                msg = sock.recv(1024)
                msg = msg.rstrip()
                msg = msg.rstrip("\n")
                if (len(msg) == 0):
                    raise Exception
                if (len(msg) > 0):
                    # print "                             \033[A"
                    sys.stdout.write(utils.CLIENT_WIPE_ME)
                    print "\r%s" % msg 
                sys.stdout.write(("%s" % utils.CLIENT_MESSAGE_PREFIX))
                sys.stdout.flush()
            else:
                message = sys.stdin.readline()
                client.send(padMessage(message))  
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush()
except Exception as e:
    pass
finally:
    # print "\033[A                           \033[A" 
    sys.stdout.write("%s\r" % utils.CLIENT_WIPE_ME)
    client.socket.close()

    
