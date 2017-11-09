"""Your awesome Distance Vector router for CS 168."""
import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16
        
class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.
        You probably want to do some additional initialization here.
        """

        self.start_timer() #Starts calling handle_timer() at correct rate

        self.ports_to_latencies = {} # Tracking latency for each port 
        self.hosts_to_ports_entries = {} # Tracking each host to port (port and latency)
        self.hosts_to_unused_ports_entries = {} # Traking each host to unused port (port and latency)

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.
        The port attached to the link and the link latency are passed
        in.
        """
        self.ports_to_latencies[port] = latency

        # Broadcast information about link to other hosts
        for destination_host in self.hosts_to_ports_entries:
            distance_vector = self.hosts_to_ports_entries[destination_host] 
            latency_to_host = distance_vector.latency

            # Send to every other port except the one the link came thru
            if distance_vector.port != port:
                if latency_to_host < INFINITY:
                    packet = basics.RoutePacket(destination_host, latency_to_host)
                    self.send(packet, port, flood=False)          
                else:
                    poison_packet = basics.RoutePacket(destination_host, INFINITY) #sending poison packet if latency is infinity
                    self.send(poison_packet, port)
                              

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.
        The port number used by the link is passed in.
        """

        # Latency of port should be updated to infinity
        self.ports_to_latencies[port] = INFINITY 
        for destination_host in self.hosts_to_unused_ports_entries:

            #Determine the prior_latency for the destination_host
            if destination_host not in self.hosts_to_ports_entries:
                prior_latency = INFINITY
            else:
                prior_latency = self.hosts_to_ports_entries[destination_host].latency

            #Take out port_entries belonging to the port of the link that goes down
            desired_port_entries = []
            for unused_port_entry in self.hosts_to_unused_ports_entries[destination_host]:
                if (unused_port_entry.port != port):
                    desired_port_entries.append(unused_port_entry)

            self.hosts_to_unused_ports_entries[destination_host] = desired_port_entries
            self.hosts_to_ports_entries[destination_host] = self.find_minimum_port_entry_latency(self.hosts_to_unused_ports_entries[destination_host]) #Find the minimum available latency

            # Send packets accordingly if latency has changed
            if prior_latency != self.get_destination_host_latency(destination_host):
                if self.get_destination_host_latency(destination_host) < INFINITY:
                    distance_vector = self.hosts_to_ports_entries[destination_host]

                    packet = basics.RoutePacket(destination_host, distance_vector.latency)
                    self.send(packet, distance_vector.port, flood=False)

                    if self.POISON_MODE:
                        poison_packet = basics.RoutePacket(destination_host, INFINITY) # poison packet
                        self.send(poison_packet, distance_vector.port)

                elif self.POISON_MODE:
                    distance_vector = self.hosts_to_ports_entries[destination_host]
                    packet = basics.RoutePacket(destination_host, distance_vector.latency)
                    self.send(packet, distance_vector.port, flood=True)
                    poison_packet = basics.RoutePacket(destination_host, INFINITY)
                    self.send(poison_packet, distance_vector.port)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.
        packet is a Packet (or subclass).
        port is the port number it arrived on.
        You definitely want to fill this in.
        """
        route_information = None

        if isinstance(packet, basics.RoutePacket):
            latency = min(packet.latency + self.ports_to_latencies[port], INFINITY)
            expire_time = api.current_time() + 15 # 15 seconds to expire a route
            route_information = RouteInformation(latency, packet.destination, expire_time, packet.src)

        elif isinstance(packet, basics.HostDiscoveryPacket):
            expire_time = float('inf') #link to host never goes down
            route_information = RouteInformation(self.ports_to_latencies[port], packet.src, expire_time, packet.src)

        #Regular packet 
        else:   
            destination_host = packet.dst
            latency_to_destination = self.get_destination_host_latency(destination_host)
            if latency_to_destination < INFINITY:
                if port != self.hosts_to_ports_entries[destination_host].port:
                    self.send(packet, self.hosts_to_ports_entries[destination_host].port) 
            return

        latency = min(route_information.latency, INFINITY)
        prior_latency = self.get_destination_host_latency(route_information.destination_host)

        if prior_latency < INFINITY:
            prior_port = self.hosts_to_ports_entries[route_information.destination_host].port
            prior_next_host_to_visit = self.hosts_to_ports_entries[route_information.destination_host].next_host_to_visit

        if route_information.destination_host not in self.hosts_to_unused_ports_entries:
            unreachable_distance_vector = DistanceVector(INFINITY, -1, float('inf'))
            self.hosts_to_unused_ports_entries[route_information.destination_host] = [unreachable_distance_vector]
        
        # Create new distance vector instance
        distance_vector = DistanceVector(latency, port, route_information.expire_time, route_information.next_host_to_visit)

        desired_port_entries = []
        for unused_port_entry in self.hosts_to_unused_ports_entries[route_information.destination_host]:
            if (unused_port_entry.next_host_to_visit != route_information.next_host_to_visit):
                desired_port_entries.append(unused_port_entry)

        self.hosts_to_unused_ports_entries[route_information.destination_host] = desired_port_entries
        self.hosts_to_unused_ports_entries[route_information.destination_host].append(distance_vector) # add new distance vector
        self.hosts_to_ports_entries[route_information.destination_host] = self.find_minimum_port_entry_latency(self.hosts_to_unused_ports_entries[route_information.destination_host])

        # Send packets accordingly
        if prior_latency < INFINITY:
            if prior_next_host_to_visit != self.hosts_to_ports_entries[route_information.destination_host].next_host_to_visit:
                distance_vector = self.hosts_to_ports_entries[route_information.destination_host]
                poison_packet = basics.RoutePacket(route_information.destination_host, INFINITY)
                self.send(poison_packet, distance_vector.port)

                if self.POISON_MODE:
                    packet = basics.RoutePacket(route_information.destination_host, latency)
                    self.send(packet, prior_port, flood=False)

        # if the latency has changed
        elif prior_latency != self.get_destination_host_latency(route_information.destination_host):
            distance_vector = self.hosts_to_ports_entries[route_information.destination_host]

            packet = basics.RoutePacket(route_information.destination_host, distance_vector.latency)
            self.send(packet, distance_vector.port, flood=True)
            poison_packet = basics.RoutePacket(route_information.destination_host, INFINITY)
            self.send(poison_packet, distance_vector.port)

    def handle_timer(self):
        """
        Called periodically.
        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.
        """
        for destination_host in self.hosts_to_unused_ports_entries:

            # look for expired ports and remove them
            desired_port_entries = []
            for unused_port_entry in self.hosts_to_unused_ports_entries[destination_host]:
                if (api.current_time() < unused_port_entry.expire_time):
                    desired_port_entries.append(unused_port_entry)

            self.hosts_to_unused_ports_entries[destination_host] = desired_port_entries
            self.hosts_to_ports_entries[destination_host] = self.find_minimum_port_entry_latency(self.hosts_to_unused_ports_entries[destination_host])

        # Send all the routes if they are under infinity
        for destination_host in self.hosts_to_ports_entries:
            if self.hosts_to_ports_entries[destination_host].latency < INFINITY: 
                distance_vector = self.hosts_to_ports_entries[destination_host]

                packet = basics.RoutePacket(destination_host, distance_vector.latency)
                self.send(packet, distance_vector.port, flood=True)
                poison_packet = basics.RoutePacket(destination_host, INFINITY)
                self.send(poison_packet, distance_vector.port)

    # Helper method to get the minimum latency of the unused port entries
    def find_minimum_port_entry_latency(self, unused_port_entries):
        minimum_port_entry = unused_port_entries[0]
        minimum_latency = unused_port_entries[0].latency

        for unused_port_entry in unused_port_entries:
            if minimum_latency > unused_port_entry.latency:
                minimum_port_entry = unused_port_entry
                minimum_latency = minimum_port_entry.latency
        return minimum_port_entry

    # Helper method to get latency to a specific destination_host
    def get_destination_host_latency(self, destination_host):
        if destination_host not in self.hosts_to_ports_entries:
            return INFINITY
        else:
            return self.hosts_to_ports_entries[destination_host].latency

class RouteInformation:
    def __init__(self, latency, destination_host, expire_time, next_host_to_visit):
        self.latency = latency
        self.destination_host = destination_host
        self.expire_time = expire_time
        self.next_host_to_visit = next_host_to_visit

class DistanceVector:
    def __init__(self, latency, port, expire_time, next_host_to_visit=None):
        self.latency = latency
        self.port = port
        self.expire_time = expire_time
        self.next_host_to_visit = next_host_to_visit
