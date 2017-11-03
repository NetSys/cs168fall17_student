class BaseWanOptimizer():
    """ Base class for WAN optimizer that implements basic functionality.

    This class includes functionality to connect clients to different
    ports, and keeps track of the network element connected to each port.

    You should NOT modify this class or turn it in with your submitted code.
    You should also not change any of the variables defined here (but you are 
    welcome to access them).
    """ 

    # The string of bits to compare the lower order 13 bits of hash to
    GLOBAL_MATCH_BITSTRING = '0111011001010'

    def __init__(self):
        # Keep track of the port that's connected to the wide area network
        # (with another WAN optimizer on the other side).
        self.wan_port = 0

        # Port to use for the next network device that connects.
        self.__next_port = 1

        # Maps the (String) address of a network element to the port the
        # element is connected to.
        self.address_to_port = {}

        # Maps each port to the network element connected to that port.
        self.port_to_network_element = {}

    def connect_wan(self, wan):
        """Connects this to a WAN."""
        self.port_to_network_element[self.wan_port] = wan

    def send(self, packet, outgoing_port):
        """ Sends the given packet out the given port.
        
        This method should only be called internally by subclasses (it should not be called
        from other middleboxes that are connected to this).
        """
        if outgoing_port >= self.__next_port or outgoing_port < 0:
            raise RuntimeError(
                ("{} is not a valid outgoing port. Outgoing port " +
                 "must be > 0 and < {}.").format(
                    outgoing_port,
                    self.__next_port))

        if outgoing_port == self.wan_port:
            # The WAN needs an addtional argument to receive, so it knows which
            # middlebox the packet came from. In reality, routers in the WAN
            # would know where packets came from based on the port the packet
            # arrived on.
            self.port_to_network_element[outgoing_port].receive(packet, self)
        else:
            self.port_to_network_element[outgoing_port].receive(packet)

    def connect(self, client, client_address):
        """ Connects client at the next unused port.

        Arguments:
          client: The client to connect.  The client must implement a receive() function that
              accepts a packet.
          client_address: A String representing the address of the given client.
        """
        port = self.__next_port
        self.__next_port = self.__next_port + 1
        self.address_to_port[client_address] = port
        self.port_to_network_element[port] = client

        # Tell the WAN that this client is connected. You can think of this as
        # being like a BGP announcement in the real Internet.
        self.port_to_network_element[self.wan_port].add_client(
            self, client_address)

    def __repr__(self):
        return (("BaseWanOptimizer<wan_port={}, address_to_port={}, " +
                "port_to_network_element={}").format(
            self.wan_port, self.address_to_port, self.port_to_network_element))

