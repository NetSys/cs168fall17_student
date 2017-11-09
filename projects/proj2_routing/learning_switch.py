"""
Your learning switch warm-up exercise for CS-168.

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0

"""

import sim.api as api
import sim.basics as basics


class LearningSwitch(api.Entity):
    """
    A learning switch.

    Looks at source addresses to learn where endpoints are.  When it doesn't
    know where the destination endpoint is, floods.

    This will surely have problems with topologies that have loops!  If only
    someone would invent a helpful poem for solving that problem...

    """

    def __init__(self):
        """
        Do some initialization.

        You probably want to do something in this method.

        """
        self.routing_table = {}

    def handle_link_down(self, port):
        """
        Called when a port goes down (because a link is removed)

        You probably want to remove table entries which are no longer
        valid here.

        """

        entities_to_delete = []
        for entity in self.routing_table: # determine which entries need to be delted
            if self.routing_table[entity] == port:
                entities_to_delete.append(entity)
        for entity in entities_to_delete: # delete those entries 
            self.routing_table.pop(entity)



    def handle_rx(self, packet, in_port):
        """
        Called when a packet is received.

        You most certainly want to process packets here, learning where
        they're from, and either forwarding them toward the destination
        or flooding them.

        """

        # The source of the packet can obviously be reached via the input port, so
        # we should "learn" that the source host is out that port.  If we later see
        # a packet with that host as the *destination*, we know where to send it!
        # But it's up to you to implement that.  For now, we just implement a
        # simple hub.

        if isinstance(packet, basics.HostDiscoveryPacket):
            # Don't forward discovery messages
            return

        dest = packet.dst
        src = packet.src

        if src not in self.routing_table:
            self.routing_table[src] = in_port

        if dest in self.routing_table:
            out_port = self.routing_table[dest]
            self.send(packet, out_port)
            return 

        # Flood out all ports except the input port
        self.send(packet, in_port, flood=True)
