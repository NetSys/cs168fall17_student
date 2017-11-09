"""Your awesome Distance Vector router for CS 168."""
#NEIL DANAIT & NITIN MANIVASAGAN (CS168-adl & CS168-afk)
import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16

class DistanceVector:
    def __init__(self, latency, port, time_to_live, next_host=None):
        self.latency = latency
        self.next_host = next_host
        self.port = port
        self.time_to_live = time_to_live

class RouteInfo:
    def __init__(self, latency, destination, time_to_live, next_host):
        self.latency = latency
        self.next_host = next_host
        self.destination = destination
        self.time_to_live = time_to_live

# class DVFilter: 
#     def __init__(self):
#         pass

#     def filter_by_time(self, elem):
#         return api.current_time() < elem.time_to_live

#     def filter_by_port(self, elem, port):
#         return elem.port != port

#     def filter_by_host(self, elem, host):
#         return elem.next_host != host

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

        self.ports_to_latencies = {} #keeps track of the lengths of the links 
        self.hosts_to_ports = {} #Stores optimal sending post for each host
        self.hosts_to_unused_ports = {} #Stores mapping between host and unused ports
        
        # self.filterer = DVFilter()

    # Helper method
    def get_latency(self, destination):
        if destination in self.hosts_to_ports:
            return self.hosts_to_ports[destination].latency
        else:
            return INFINITY

    def advertise_route_to_neighbors(self, destination):
        """
        Broadcast the route to all appropriate neighbors.
        """
        distance_vector = self.hosts_to_ports[destination]
        self.handle_proper_packet(distance_vector.port, destination, distance_vector.latency, True)
        self.handle_poison_packet(distance_vector.port, destination)

    def handle_proper_packet(self, port, destination, latency, flood=False):
        """
        Send packet through respective port.
        """
        packet = basics.RoutePacket(destination=destination, latency=latency)
        self.send(packet, port=port, flood=flood)

    def handle_poison_packet(self, port, destination):
        """
        Poison packet through respective port.
        """
        if self.POISON_MODE:
            poison_packet = basics.RoutePacket(destination=destination, latency=INFINITY)
            self.send(poison_packet, port=port)

    def find_minium_latency_unused_ports(self, ports):

        min_port = ports[0]
        min_latency = min_port.latency

        for port in ports:
            if port.latency < min_latency:
                min_port = port
                min_latency = port.latency 
        return min_port

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.
        The port attached to the link and the link latency are passed in.
        """
        #Add the port to latency mapping to the dictionary
        self.ports_to_latencies[port] = latency

        #When new link comes up, let the other hosts know about it
        for dest in self.hosts_to_ports.keys():
            distance_vector = self.hosts_to_ports[dest] 
            host_latency = distance_vector.latency

            #only send to those links that are not the one coming up
            if distance_vector.port != port:
                if host_latency < INFINITY:
                    packet = basics.RoutePacket(dest, latency)
                    self.send(packet, port)
                else:
                    if self.POISON_MODE == True:
                        poison_packet = basics.RoutePacket(dest, INFINITY)
                        self.send(poison_packet, port)          

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.
        The port number used by the link is passed in.
        """
        # Update the latency for this port to something greater than INFINITY
        self.ports_to_latencies[port] = INFINITY + 1

        for dest in self.hosts_to_unused_ports:

            #Determine the prior distance

            prior_distance = INFINITY
            if dest in self.hosts_to_unused_ports:
                prior_distance = self.hosts_to_ports[dest].latency

            #Take out all the entries that have the same port as the one being passed in
            self.hosts_to_unused_ports[dest] = [host for host in self.hosts_to_unused_ports[dest] if host.port != port] 
            self.hosts_to_ports[dest] = self.find_minium_latency_unused_ports(self.hosts_to_unused_ports[dest])

            if prior_distance != self.get_latency(dest):
                # if self.get_latency(dest) < INFINITY:

                distance_vector = self.hosts_to_ports[dest]

                # Send normal route packet
                packet = basics.RoutePacket(dest, distance_vector.latency)
                self.send(packet, port)

                # Send poison packet if POISON_MODE is true
                if self.POISON_MODE == True:
                    poison_packet = basics.RoutePacket(dest, INFINITY)
                    self.send(poison_packet, port)  

                # elif self.POISON_MODE == True:
                #     self.advertise_route_to_neighbors(destination)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.
        packet is a Packet (or subclass).
        port is the port number it arrived on.
        You definitely want to fill this in.
        """
        route_info = None

        if isinstance(packet, basics.RoutePacket):
            latency = min(self.ports_to_latencies[port] + packet.latency, INFINITY)
            time_to_live = api.current_time() + 15 
            route_info = RouteInfo(latency, packet.destination, time_to_live, packet.src)

        elif isinstance(packet, basics.HostDiscoveryPacket):
            time_to_live = float('inf') #time to live is infinity for hosts
            route_info = RouteInfo(self.ports_to_latencies[port], packet.src, time_to_live, packet.src)

        # Regular Packet, if route to host less than infinity exists
        else:   
            destination = packet.dst
            latency = self.get_latency(destination)
            if latency < INFINITY:
                if port != self.hosts_to_ports[destination].port:
                    self.send(packet, self.hosts_to_ports[destination].port)

        if route_info != None:
            latency = min(route_info.latency, INFINITY)
            prior_latency = self.get_latency(route_info.destination)

            if prior_latency != INFINITY:
                prior_port = self.hosts_to_ports[route_info.destination].port
                prior_next_host = self.hosts_to_ports[route_info.destination].next_host

            #Add it to the unused entries dictionary if not already in there
            if route_info.destination not in self.hosts_to_unused_ports:
                unreachable_distance_vector = DistanceVector(INFINITY, -1, float('inf'))
                self.hosts_to_unused_ports[route_info.destination] = [unreachable_distance_vector]
            
            #Create a new distance vector instance and add it to the respective destination mapping
            distance_vector = DistanceVector(latency, port, route_info.time_to_live, route_info.next_host)
            self.hosts_to_unused_ports[route_info.destination] = [host for host in self.hosts_to_unused_ports[route_info.destination] if (host.next_host != route_info.next_host)]
            self.hosts_to_unused_ports[route_info.destination].append(distance_vector)
            self.hosts_to_ports[route_info.destination] = self.find_minium_latency_unused_ports(self.hosts_to_unused_ports[route_info.destination])

            if prior_latency != INFINITY:
                if prior_next_host != self.hosts_to_ports[route_info.destination].next_host:

                    if self.POISON_MODE:
                        poison_packet = basics.RoutePacket(route_info.destination, INFINITY)
                        self.send(poison_packet, self.hosts_to_ports[route_info.destination].port)

                        packet = basics.RoutePacket(route_info, latency)
                        self.send(packet, prior_port)

            elif prior_latency != self.get_latency(route_info.destination):
                # self.advertise_route_to_neighbors(route_info.destination)

                distance_vector = self.hosts_to_ports[route_info.destination]

                packet = basics.RoutePacket(route_info, distance_vector.latency)
                self.send(packet, distance_vector.port, flood=True)

                if self.POISON_MODE:
                    poison_packet = basics.RoutePacket(route_info.destination, INFINITY)
                    self.send(poison_packet, distance_vector.port)


    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """

        for dest in self.hosts_to_unused_ports:
            self.hosts_to_unused_ports[dest] = [host for host in self.hosts_to_unused_ports[dest] if api.current_time() != host.time_to_live] 
            self.hosts_to_ports[dest] = self.find_minium_latency_unused_ports(self.hosts_to_unused_ports[dest])

        #Send the reachable routes (must be less than infinity)
        for dest in self.hosts_to_ports:
            if self.hosts_to_ports[dest].latency < INFINITY: 
                distance_vector = self.hosts_to_ports[dest] 
                host_latency = distance_vector.latency

                distance_vector = self.hosts_to_ports[dest]

                # Send normal route packet
                packet = basics.RoutePacket(dest, host_latency)
                self.send(packet, distance_vector.port)

                # Send poison packet if POISON_MODE is true
                if self.POISON_MODE == True:
                    poison_packet = basics.RoutePacket(dest, INFINITY)
                    self.send(poison_packet, distance_vector.port)  
