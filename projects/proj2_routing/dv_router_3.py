"""Your awesome Distance Vector router for CS 168."""
#NEIL DANAIT & NITIN MANIVASAGAN (CS168-adl & CS168-afk)
import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16

class DV:
    def __init__(self, latency, port, expire_time, next_host=None):
        self.latency = latency
        self.next_host = next_host
        self.port = port
        self.expire_time = expire_time

class RouteInfo:
    def __init__(self, latency, destination, expire_time, next_host):
        self.latency = latency
        self.next_host = next_host
        self.destination = destination
        self.expire_time = expire_time

class DVFilter: 
    def __init__(self):
        pass

    def filter_by_time(self, elem):
        return api.current_time() < elem.expire_time

    def filter_by_port(self, elem, port):
        return elem.port != port

    def filter_by_host(self, elem, host):
        return elem.next_host != host

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

        self.host_to_entry = {} #Mapping between host and used entries
        self.host_to_unused_entry = {} #Mapping between host and unused entries
        self.port_to_latency = {} #Mapping between ports and respective latency
        
        self.filterer = DVFilter()

    def retrieve_latency(self, destination):
        """
        Get the latency associated with a particular destination.
        """
        #Confirm that the destination's latency is not infinity prior to returning it, else return infinity
        if destination in self.host_to_entry:
            return min(INFINITY, self.host_to_entry[destination].latency)
        else:
            return INFINITY

    def advertise_route_to_neighbors(self, destination):
        """
        Broadcast the route to all appropriate neighbors.
        """
        distance_vector = self.host_to_entry[destination]
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

    def find_min_latency_entry(self, entries):
        """
        Finds the minimum latency among all the unused entries.
        """
        #Declare minimum entry/latency as first entry/latency
        min_entry = entries[0]
        min_latency = entries[0].latency

        #Update minimum attributes if needed
        for entry in entries:
            if min_latency > entry.latency:
                min_entry = entry
                min_latency = min_entry.latency
        return min_entry

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.
        The port attached to the link and the link latency are passed in.
        """
        #Add the port to latency mapping to the dictionary
        self.port_to_latency[port] = latency

        #Notify all other hosts about the link
        for destination in self.host_to_entry.keys():
            distance_vector = self.host_to_entry[destination] 
            host_latency = distance_vector.latency

            #Handle the case where the port for that vector does not equal the port associated with the new link
            if distance_vector.port != port:
                if host_latency < INFINITY:
                    self.handle_proper_packet(port, destination, host_latency)
                else:
                    self.handle_poison_packet(port, destination)            

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.
        The port number used by the link is passed in.
        """
        #Update the latency of the port in the dictionary to >= infinity
        self.port_to_latency[port] = INFINITY + 1
        for destination in self.host_to_unused_entry.keys():

            #Determine the prior distance, infinity if not in the dictionary
            if destination not in self.host_to_entry.keys():
                prior_distance = INFINITY
            else:
                prior_distance = self.host_to_entry[destination].latency

            #Take out all the entries that have the same port as the one being passed in
            self.host_to_unused_entry[destination] = [entry for entry in self.host_to_unused_entry[destination] if self.filterer.filter_by_port(entry, port)] 
            self.host_to_entry[destination] = self.find_min_latency_entry(self.host_to_unused_entry[destination]) #Find the minimum available latency

            if prior_distance != self.retrieve_latency(destination):
                if self.retrieve_latency(destination) < INFINITY:
                    self.advertise_route_to_neighbors(destination)
                elif self.POISON_MODE:
                    self.advertise_route_to_neighbors(destination)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.
        packet is a Packet (or subclass).
        port is the port number it arrived on.
        You definitely want to fill this in.
        """
        route_info = None

        #Handle the case where it is a Route Packet
        if isinstance(packet, basics.RoutePacket):
            latency = min(packet.latency + self.port_to_latency[port], INFINITY)
            expire_time = api.current_time() + 15 #Give the 15 second threshold
            route_info = RouteInfo(latency, packet.destination, expire_time, packet.src)

        #Handle the case where it is a Discovery Packet
        elif isinstance(packet, basics.HostDiscoveryPacket):
            expire_time = float('inf') #Default infinity
            route_info = RouteInfo(self.port_to_latency[port], packet.src, expire_time, packet.src)

        #Typical else edge case
        else:   
            destination = packet.dst
            latency_to_destination = self.retrieve_latency(destination)
            if latency_to_destination < INFINITY:
                if port != self.host_to_entry[destination].port:
                    self.send(packet, port=self.host_to_entry[destination].port) 


        if route_info != None:
            latency = min(route_info.latency, INFINITY)
            prior_latency = self.retrieve_latency(route_info.destination)

            if prior_latency != INFINITY:
                prior_port = self.host_to_entry[route_info.destination].port
                prior_next_host = self.host_to_entry[route_info.destination].next_host

            #Add it to the unused entries dictionary if not already in there
            if route_info.destination not in self.host_to_unused_entry:
                unreachable_distance_vector = DV(INFINITY, -1, float('inf'))
                self.host_to_unused_entry[route_info.destination] = [unreachable_distance_vector]
            
            #Create a new distance vector instance and add it to the respective destination mapping
            distance_vector = DV(latency, port, route_info.expire_time, route_info.next_host)
            self.host_to_unused_entry[route_info.destination] = [entry for entry in self.host_to_unused_entry[route_info.destination] if self.filterer.filter_by_host(entry, route_info.next_host)]
            self.host_to_unused_entry[route_info.destination].append(distance_vector)
            self.host_to_entry[route_info.destination] = self.find_min_latency_entry(self.host_to_unused_entry[route_info.destination])

            if prior_latency != INFINITY:
                if prior_next_host != self.host_to_entry[route_info.destination].next_host:
                    self.handle_poison_packet(self.host_to_entry[route_info.destination].port, route_info.destination)
                    if self.POISON_MODE:
                        self.handle_proper_packet(prior_port, route_info.destination, latency)

            #If the prior latency does not equal the latency associated with the current destination, broadcast accordingly
            elif prior_latency != self.retrieve_latency(route_info.destination):
                self.advertise_route_to_neighbors(route_info.destination)

    def handle_timer(self):
        """
        Called periodically.
        When called, your router should send host_to_entrys to neighbors.  It also might
        not be a bad place to check for whether any entries have expired.
        """
        for destination in self.host_to_unused_entry:
            self.host_to_unused_entry[destination] = [entry for entry in self.host_to_unused_entry[destination] if self.filterer.filter_by_time(entry)]
            self.host_to_entry[destination] = self.find_min_latency_entry(self.host_to_unused_entry[destination])

        #Send the reachable routes (must be less than infinity)
        for destination in self.host_to_entry:
            if self.host_to_entry[destination].latency < INFINITY: 
                self.advertise_route_to_neighbors(destination)
  
