import tcp_packet
import utils

# String that marks the end of a filename. This sequence of characters
# cannot be in the filename (otherwise it will be incorrectly interpreted
# as the end of the filename).
FILENAME_DELIMITER = "*&-02~:"

class EndHost():
    """ Represents a client connected to the network.

    Attributes:
        identifier: Name of the client (used only for debug messages).
        ip_address: Source address of the client.
        gateway_middlebox: Middlebox that all of the client's packets are
            send through before being forwarded to the wide area network. 
    """
    def __init__(self, identifier, ip_address, gateway_middlebox):
        self.identifier = identifier
        self.ip_address = ip_address
        self.gateway_middlebox = gateway_middlebox
        self.gateway_middlebox.connect(self, self.ip_address)
        # Array to write output data to.  If this is empty, it means that no data
        # has been received.
        self.received_data = []

    def send_file(self, input_filename, destination_ip_address):
        """ Sends the given file to the given destination.

        The input_filename is transmitted first, followed by FILENAME_DELIMITER.
        
        Breaks the file up into packets in order to send it.
        """
        f = open(input_filename, 'rb')
        # The filename followed by the delimiter is the first thing sent.
        packet_data = input_filename + FILENAME_DELIMITER
        assert len(packet_data) <= utils.MAX_PACKET_SIZE
        finished_reading = False
        while not finished_reading:
            # Read in a packet worth of data.
            while len(packet_data) < utils.MAX_PACKET_SIZE:
                remaining_data = utils.MAX_PACKET_SIZE - len(packet_data)
                new_data = f.read(remaining_data)
                if not new_data:
                    # There's no data left in the file.
                    finished_reading = True
                    break
                packet_data = packet_data + new_data

            # Send the current packet.
            # Note that this packet may be empty if the file is done reading
            # but we still need to send a FIN packet.
            packet = tcp_packet.Packet(
                self.ip_address, 
                destination_ip_address,
                is_raw_data = True,
                is_fin = finished_reading,
                payload = packet_data)
            self.gateway_middlebox.receive(packet)
            packet_data = ""

        f.close()

    def receive(self, packet):
        """ Handles receiving a packet and writing data to a file.
        
        This function handles determining the filename, and saving data
        (as it is received) to a file named identifier-filename, where
        identifier is the name of this client, and filename is the filename
        received.
        """
        self.sanity_check(packet)
        self.received_data.append(packet.payload)

        # If this is the last packet of the transfer, save the file 
        if packet.is_fin:
            self.save_to_file()

    def save_to_file(self):
        data = "".join(self.received_data)
        data_start = 0

        # Extract the filename from the file
        filename_end = data.find(FILENAME_DELIMITER)
        # If filename does not exist, raise an error
        if filename_end == -1:
            raise RuntimeError("Filename delimiter could not be found." +
                " This probably means that the " +
                "file was corrupted. File received was {}".format(
                    data))
        filename = data[:filename_end]
        # Open the an output file using receiver's id and filename
        full_filename = "{}-{}".format(self.identifier, filename)
        output_file = open(full_filename, "wb")
        data_start = filename_end + len(FILENAME_DELIMITER)

        # Write the received data to a file.
        packet_data = data[data_start:]
        output_file.write(packet_data)

        # close the file and empty out the array to 
        # allow receiving new files
        output_file.close()
        self.received_data = []

    def sanity_check(self, packet):
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




