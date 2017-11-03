class Packet():
    """ Represents a packet in the network.

    This packet is similar to a TCP packet: it has a source IP address,
    destination IP address, size and payload.  For simplicity,
    the packet just has a single IP address, rather than a port (which would be
    in a real TCP packet header). It also has two flags, is_fin and is_label,
    which could be fit into the flags field of a TCP packet (a trick often
    used to shoehorn additional information into a TCP header).

    Attributes:
        src: The sender of the packet
        dest: The final destination the packet is meant for
        is_raw_data: Whether the packet represents raw data. If this is false,
            the packet payload is a hash of data that the middlebox should
            have already received.
        is_fin: Whether this packet is the last one in the stream of data.
        payload: The actual data/bytes in the packet
    """

    def __init__(self, src, dest, is_raw_data, is_fin, payload):
        self.src = src
        self.dest = dest
        self.is_raw_data = is_raw_data
        self.is_fin = is_fin
        self.payload = payload

    def size(self):
        return len(self.payload)

    def __repr__(self):
        """ Returns a string representation of the packet (useful for printing).
        """
        return ("TcpPacket<src={}, dest={}, is_raw_data={}, is_fin={}, "
            "size={}>").format(
                self.src, self.dest, self.is_raw_data, self.is_fin,
                self.size())
