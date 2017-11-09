import socket
import sys
import utils
import select

class Server(object):

    def __init__(self, port):
        self.socket = socket.socket()
        self.socket.bind(("", int(port)))
        self.socket.listen(5)
        self.port = port

        self.all_sockets = []
        self.all_sockets.append(self.socket)

        self.channels_to_clients = {}
        self.clients_to_channels = {}
        self.clients_to_names = {}

    def padMessage(self, message):
        original_message_length = len(message)
        return message.ljust(utils.MESSAGE_LENGTH - original_message_length + 1)
    
    def start(self):

        try:
            while True:
                read_sockets, write_sockets, exception_sockets = select.select(self.all_sockets, [], [])

                for sock in read_sockets:
                    if sock == self.socket:
                        (new_socket, address) = self.socket.accept()
                        self.all_sockets.append(new_socket)
                        name = new_socket.recv(1024).rstrip()
                        # print("name")
                        # print(name)
                        self.clients_to_names[new_socket] = name
                        # print(self.clients_to_names[new_socket])
                    else:
                        msg = sock.recv(1024)
                        msg = msg.rstrip()
                        msg = msg.rstrip("\n")

                        if len(msg) == 0:
                            # sock.shutdown(socket.SHUT_RDWR)
                            #sock.close()
                            self.disconnectClient(sock)
                            continue

                        if (msg[0] == '/'):
                            command_parts = msg.split(" ")
                            command = command_parts[0]
                            if (command == "/list"):
                                if (len(command_parts) > 1):
                                    sock.send(self.padMessage(utils.SERVER_INVALID_CONTROL_MESSAGE.format(msg)))
                                else:
                                    self.sendAllChannels(sock)
                            elif (command == "/join"):
                                if (len(command_parts) == 1):
                                    sock.send(self.padMessage(utils.SERVER_JOIN_REQUIRES_ARGUMENT))
                                else:
                                    channel_name = command_parts[1:len(command_parts)]
                                    channel_name = ' '.join(channel_name)
                                    self.joinChannel(sock, channel_name)
                            elif (command == "/create"):
                                if (len(command_parts) == 1):
                                    sock.send(self.padMessage(utils.SERVER_CREATE_REQUIRES_ARGUMENT))
                                else:
                                    channel_name = command_parts[1:len(command_parts)]
                                    channel_name = ' '.join(channel_name)
                                    self.createChannel(sock, channel_name)
                            else:
                                sock.send(self.padMessage(utils.SERVER_INVALID_CONTROL_MESSAGE.format(msg)))
                        else:
                            if sock not in self.clients_to_channels:
                                sock.send(self.padMessage(utils.SERVER_CLIENT_NOT_IN_CHANNEL))
                            else:
                                self.broadcastMessage(sock, msg, False) #Normal message
        finally:
            self.all_sockets.remove(self.socket)
            for client in self.all_sockets:
                message = utils.CLIENT_SERVER_DISCONNECTED.format("127.0.0.1", self.port)
                message = self.padMessage(message)
                client.send(message)
            self.socket.close()

    def disconnectClient(self, client_socket):

        if client_socket in self.clients_to_channels:
            current_channel = self.clients_to_channels[client_socket]
            client_name = self.clients_to_names[client_socket]
            clients_in_channels = self.channels_to_clients[current_channel]
            clients_in_channels.remove(client_socket)
            del self.clients_to_channels[client_socket]
            for client in clients_in_channels:
                message = self.padMessage(utils.SERVER_CLIENT_LEFT_CHANNEL.format(client_name))
                client.send(message)

    def sendAllChannels(self, client_socket):
        message = ""
        for channel in self.channels_to_clients.keys():
            message += "%s\n" % channel

        if (len(message) > 0):
            message = message[:-1]
            message = self.padMessage(message)
            client_socket.send(message)

        # original_message_length = len(message)
        # message = message.ljust(utils.MESSAGE_LENGTH - original_message_length + 1) #pad the message


    def createChannel(self, client_socket, channel_name):
        if channel_name in self.channels_to_clients: #if channel already exists
            message = utils.SERVER_CHANNEL_EXISTS.format(channel_name)
            client_socket.send(self.padMessage(message))
        else:
            self.disconnectClient(client_socket)
            if client_socket in self.clients_to_channels: #if a client is already in a channel
                current_channel = self.clients_to_channels[client_socket]
                self.channels_to_clients[current_channel].remove(client_socket)
                self.channels_to_clients[channel_name] = [client_socket]
                self.clients_to_channels[client_socket] = channel_name
            else:
                self.channels_to_clients[channel_name] = [client_socket]
                self.clients_to_channels[client_socket] = channel_name
        

    def joinChannel(self, client_socket, channel_name):

        if ((client_socket in self.clients_to_channels) and (self.clients_to_channels[client_socket] == channel_name)):
            return

        self.disconnectClient(client_socket)
        if channel_name not in self.channels_to_clients: #if channel doesn't exist
            message = utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name)
            client_socket.send(self.padMessage(message))
            return
        else: 
            if client_socket in self.clients_to_channels: #if a client is already in a channel
                current_channel = self.clients_to_channels[client_socket]
                self.channels_to_clients[current_channel].remove(client_socket)
                self.channels_to_clients[channel_name].append(client_socket)
                self.clients_to_channels[client_socket] = channel_name
            else: #if client is not in a channel
                self.channels_to_clients[channel_name].append(client_socket)
                self.clients_to_channels[client_socket] = channel_name

            # Let other clients in channel know that someone has joined
            client_name = self.clients_to_names[client_socket]
            message = utils.SERVER_CLIENT_JOINED_CHANNEL.format(client_name) 
            self.broadcastMessage(client_socket, message, True)

    def broadcastMessage(self, client_socket, message, joinFlag):
        # message = self.padMessage(message)
        channel_name = self.clients_to_channels[client_socket]
        # print(channel_name)
        clients = self.channels_to_clients[channel_name]
        client_name = self.clients_to_names[client_socket]
        original_message = message
        for client in clients:

            if client == client_socket: #send empty message to client that joined or sent message
                continue

            if (joinFlag):
                message = "{0}".format(original_message)
            else:
                message = "[%s] %s" % (client_name, original_message)

            message = self.padMessage(message) 
            client.send(message)
    
args = sys.argv
if len(args) != 2:
    print "Please supply a port."
    sys.exit()
server = Server(args[1])
server.start()
