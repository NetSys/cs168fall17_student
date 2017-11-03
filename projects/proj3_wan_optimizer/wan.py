import utils

class Wan():
    """ Represents a wide area network (WAN).

    For the purposes of this assignment, a wide area network is connected to
    exactly two middleboxes, and the WAN only forwards packets between those
    two middleboxes.  This is intended to represent a scenario where some
    entity (e.g., a company) has sites in two places that are connected
    by a wide area network, and uses WAN optimizer middleboxes on each side
    to optimize (i.e., reduce) how much traffic is sent over the WAN.

    The WAN also does some sanity checking of packets: it makes sure each
    field in the packet is of the expected type, that the source address
    is consistent with the direction that the packet is coming from,
    and that the destination address matches one of the places where the
    packet is headed.

    The WAN keeps track of how many bytes have been sent over it, which can
    be used to check how the wan optimizers on either side are affecting
    the total amount of traffic that's sent.
    """

    def __init__(self, wan_optimizer_1, wan_optimizer_2):
        self.__wan_optimizer_1 = wan_optimizer_1
        self.__wan_optimizer_1.connect_wan(self)
        self.__wan_optimizer_2 = wan_optimizer_2
        self.__wan_optimizer_2.connect_wan(self)

        # Tracks the total bytes that have been sent across the network.
        self.__total_bytes_sent = 0

        # Maps each wan optimizer to the clients connected to that wan
        # optimizer. Used to verify that source and destination addresses
        # in packets being sent make sense.
        self.__wan_optimizer_to_clients = {
            self.__wan_optimizer_1: [],
            self.__wan_optimizer_2: []}

    def add_client(self, wan_optimizer, client_address):
        """ Notifies the WAN about the location of a client.

        In the real world, this would be implied by the address (e.g., the
        address would match a particular subnet, so routers in the WAN know
        how to route to the address.
        """
        self.__wan_optimizer_to_clients[wan_optimizer].append(client_address)

    def get_total_bytes_sent(self):
        """ Returns the total # of bytes that have been sent on the WAN."""
        return self.__total_bytes_sent

    def sanity_check(self, packet, previous_hop):
        """ Checks that the packet header makes sense. """
        # Make sure all of the packet's header fields are the correct type.
        if not isinstance(packet.src, str):
            raise RuntimeError("Packet src must be a string; was {}".format(
                packet.src))
        if not isinstance(packet.dest, str):
            raise RuntimeError("Packet dest must be a string; was {}".format(
                packet.dest))
        if not isinstance(packet.is_raw_data, bool):
            raise RuntimeError("Packet is_raw_data must be a bool; was " +
                               str(packet.is_raw_data))
        if not isinstance(packet.is_fin, bool):
            raise RuntimeError("Packet is_fin must be a bool; was " +
                               str(packet.is_fin))
        if not isinstance(packet.payload, str):
            raise RuntimeError("Packet payload must be a string; was " +
                               str(packet.payload))

        # Check that the packet isn't larger than the maximum size.
        if packet.size() > utils.MAX_PACKET_SIZE:
            raise RuntimeError(("Received packet {} with length {}, " +
                                "which is greater than the maximum packet " +
                                "size.").format(
                packet, len(packet.payload)))

        # Make sure the packet came from one of the two wan optimizers.
        if previous_hop not in self.__wan_optimizer_to_clients:
            raise RuntimeError(
                ("Wide area network received packet {} that " +
                 "is not from either of the connected middleboxes. Clients " +
                 "cannot send directly to the wide area " +
                 "network.").format(packet))

        # Check that the packet source address is consistent with where the
        # packet came from.
        if packet.src not in self.__wan_optimizer_to_clients[previous_hop]:
            raise RuntimeError(
                ("Packet src is {}, which is not connected " +
                 "to the middlebox that the packet came from ({}). This " +
                 "probably means your middlebox is forwarding packets to " +
                 "the WAN that should be forwarded to an attached " +
                 "client.").format(
                    packet.src,
                    previous_hop))

        # Check that the packet destination address is consistent with where
        # the packet is going.
        if previous_hop == self.__wan_optimizer_1:
            other_wan_optimizer = self.__wan_optimizer_2
        else:
            other_wan_optimizer = self.__wan_optimizer_1
        if packet.dest not in self.__wan_optimizer_to_clients[other_wan_optimizer]:
            raise RuntimeError(("Packet dest is {}, which is not connected " +
                                "to the destination middlebox ({})").format(
                packet.dest, other_wan_optimizer))

    def receive(self, packet, previous_hop):
        """ Sends packets across the wide area network. """
        # Do some sanity checking of the packet.
        self.sanity_check(packet, previous_hop)
        if previous_hop == self.__wan_optimizer_1:
            self.__total_bytes_sent += packet.size()
            self.__wan_optimizer_2.receive(packet)
        elif previous_hop == self.__wan_optimizer_2:
            self.__total_bytes_sent += packet.size()
            self.__wan_optimizer_1.receive(packet)
