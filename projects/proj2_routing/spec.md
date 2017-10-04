# Routing

In this assignment, you'll implement distance-vector routing, a distributed routing algorithm where multiple routers cooperate to transport packets to their destinations efficiently. Your routing algorithm will run on each router within a simulated network. Each router will exchange messages with neighboring routers and hosts to construct a forwarding table. As the network topology changes, your routing algorithm will update the forwarding tables to maintain connectivity.

#### Logistics

- This project is due on Friday 10/6 at 11:59pm.
- This project should be completed **individually**. You may share your tests with anyone in the class.
- The skeleton code for this project is available on [GitHub](https://github.com/NetSys/cs168fall17_student/blob/master/projects/proj2_routing/). You can download the code manually from that page, or use Git.
- You'll submit your code using `ok`. You should submit two files: one named `learning_switch.py` and one named `dv_router.py`. You should write your own tests by adding files to `tests/` and `topos/`, but no need to submit them. Don't modify `simulator.py` or anything in `sim/`. More detailed submission instructions can be found in the [submission details](#submission-details) section.
- You may develop this project using the operating system of your choice (Windows, Mac OS X and Linux systems should all work) and using either Python 2 or Python 3. **However, make sure your code runs using Python 2 on the instructional (Unix) machines, because this is what we will be using to grade the code**

#### Resources

- If you have questions, first take a look at the [FAQ page](faq.md).  If your question isn't answered there, post to Piazza.
- The distance-vector routing protocol you'll implement is similar to RIP. [RFC 2453](https://www.ietf.org/rfc/rfc2453.txt) describes RIPv2 and might be helpful for understanding the subtleties of this assignment. It covers several features of RIP that your distance-vector router should also implement, particularly split horizon and split horizon with poisoned reverse (3.4.3), and timed updates and route expiration (3.8). RIP has a few features that we don't require you to implement for this assignment, including triggered updates (3.4.4) and hold-down.

## Background on routing

Networks deliver packets between hosts by passing the packets from the source host, through a sequence of routers/switches, and finally to the destination host. Since all packets are eventually destined for a host, you should only compute routes to hosts, not to other routers.

Network entities (hosts and routers/switches) are connected using links. A link consists of a port on one device, a cable, and a port on the other device. (Note that these ports are different from the logical ports in transport layer protocols like TCP and UDP.)

Each device is only aware of its own ports, so when a link malfunctions, it is possible that one device may detect the link is down but the other may not. Links may also be flaky, in which case they may drop packets intermittently.

## Overview of the network simulator

The network simulator models network entities and the links between them as Python objects. It provides an API that you will use to implement your router and to write tests.

You will be creating subclasses of the `Entity` class (`sim/api.py`). Each `Entity` subclass models a different type of device in the network (like a host or your router) and has a number of ports, each of which may be connected to another neighbor `Entity`. Entities send and receive `Packet`s (`sim/api.py`) to and from their neighbors.

The simulator comes with some automated tests, which you can run using `python test_suite.py`. You can also test your code interactively using `simulator.py` and visualize its progress using NetVis.

See the [simulator guide](simulator_guide.md) for more details.

## Part 1: Learning Switch

To get started, you will implement a learning switch, which learns the location of hosts by monitoring traffic. At first, the switch simply floods any packet it receives to all of its neighbors, like a hub.  For each packet it sees, it remembers for the sender `S` the port that the packet came in on. Later, if it receives packets destined to `S`, it only forwards the packet out on the port that packets from `S` previously came in on. This is because if packets from `S` *arrived* on port 3, then port 3 must be able to reach `S` -- you can send *to* `S` via port 3. We've provided a skeleton `learning_switch.py` for you to modify.

Recall from class that a learning switch is not a very effective routing technique; its greatest shortcoming is that it breaks when the network has loops.  That's why our next step will be to implement a more capable distance vector router.  That's also why you only need to test it on topologies without loops.

Additionally, a learning switch that never exchanges routing messages will not be able to avoid routing loops in case of topology change (e.g., if a host moves from one switch to another). You therefore only need to test on static topologies without failures.

## Part 2: Distance-Vector Router

We've provided a skeleton `dv_router.py` file with the beginnings of a `DVRouter` class for you to flesh out, implementing your distance vector router. The `DVRouter` class inherits from the `DVRouterBase` class, which adds a little bit to the basic `Entity` class.  Specifically, it adds a `POISON_MODE` flag and a `handle_timer` method.  When your router's `self.POISON_MODE` is `True`, your router should send poisoned routes and poisoned reverses (and when `False`, it should not).  The `handle_timer` method is called periodically.  When it is called, your router should send all its routes to its neighbors.

Ultimately, you will need to override some or all of the `handle_rx`, `handle_timer`, `handle_link_up`, and `handle_link_down` methods.  Feel free to add whatever other methods you like.  Note that your `DVRouter` instances should *only* communicate with other `DVRouter` instances via the sending of packets.  Global variables, class variables, calling methods on other instances, etc. are not allowed -- each `DVRouter` instance should be entirely standalone.

Your `handle_rx` will need to deal with two types of packets specially (that is, two subclasses of `Packet`), which are listed below.  All other packets are data packets which need to be sent on an appropriate port based on the current routing table. You can differentiate packet types using Python's `isinstance()`.  Note that while you can create custom packet types for your own testing or amusement, you should not rely on any such modifications for your router to work.  Don't add any attributes besides the ones they already have.

- `basics.HostDiscoveryPacket`s are sent automatically by host entities when they are attached to a link.  Your `DVRouter` should monitor for these packets so that it knows what hosts exist and where they are attached.  Your `DVRouter` should never send or forward `HostDiscoveryPacket`s.

- `basics.RoutePacket` contains a single route.  It has a `destination` attribute (the `Entity` that the route is routing to) and a `latency` attribute which is the distance to the `destination`.  Take special note that `RoutePacket.destination` and `Packet.dst` are not the same thing.  They are essentially at different layers.  `dst` is like an L2 address -- it's where this particular packet is destined (and since `RoutePacket`s should never be directly forwarded, this should probably be `None`).  `destination` is at a higher layer and specifies which destination this route is for.

Your implementation should perform the following:

- **Expire routes**. On receiving a `RoutePacket` message from a neighbor, your router should remember the route for approximately 15 seconds (but not less than that), after which it should be treated as expired. You can use your router's `self.ROUTE_TIMEOUT` constant.
- **Handle link weights**.  Your router should use minimum weight/cost/latency paths -- not just hop counts.  Thus, you need to locally track the link latencies you are given by `handle_link_up`, you need to compute correct weights when sending routes to neighbors, and you need to select the lowest cost routes available when forwarding.
- **Timed updates**. In response to a timer, your router should send its routes to its neighbors (in the form of `RoutePacket`s).  This refreshes the route entries and keeps them from expiring.
- **Eagerly initialize new neighbors**. As soon a link comes up, your router should share its routes with the new neighbor.
- **Poison mode**. When poison mode is turned on, your router should implement *route poisoning* and *split horizon with poisoned reverse*. Route poisoning means that if your router has sent a route which is now removed, it should advertise a "poison" version of that route with an infinite cost to promote its immediate removal rather than waiting for it to expire. Split horizon with poisoned reverse is described below.
- **Split horizon**. Don't advertise a route back onto the port it came from. When poison mode is turned off, this should result in *simple split horizon*, where your router simply does not advertise such routes and instead waits for them to expire. When poison mode is turned on, this should result in *split horizon with poisoned reverse*, where your router instead advertises such routes as having infinite cost.
- **Don't "hairpin" a packet**. Never forward a data packet back out the port it arrived on... this is seldom helpful.
- **Implement infinity as 16**. Note that split horizon with poisoned reverse is not sufficient for preventing count-to-infinity in some cases (see lecture notes for examples). To deal with such un-preventable cases, your distance vector router should treat destinations with long distances as unreachable. For this project, your implementation should stop counting at 16 and remove routes to corresponding destinations. We will make sure that no valid path in our test scenarios exceeds this length.
- **Deal with changes**. Your solution should quickly and efficiently generate new, optimal routes when the topology changes (e.g., when links are added or removed). For example, it shouldn't take more than 5 seconds (one timer interval) for the route to a new host to propagate from one router to its neighbors. Note that you only need to send routing updates in `handle_timer` (i.e., you are only required to implement timed updates); you do not need to send routing updates immediately when other events happen, but you can if you want (i.e., triggered updates are optional).

## Rules

- **You should not modify the simulator code**. Though Python is self-modifying and therefore you could write code that rewrites the simulator, we won't award credit for solutions that subvert the assignment in this way. Additionally, don't override any of the methods which aren't clearly intended to be overridden, and don't alter any constants.

- **Your learning switch and router should only communicate with other instances via the sending of packets.**  Global variables, class variables, calling methods on other instances, etc. are not allowed -- each instance should be entirely standalone.

- **The project is designed to be solved independently. You may not share submitted code with anyone** You may discuss the assignment requirements or your solutions away from a computer and without sharing code, but you should not discuss the detailed nature of your solution (e.g., what algorithm was used to compute the routing table). You may share your test code with anyone in the class. Please don't put any code from this project in a public repository.

## Tips

Some things to do to help you get started

- Read `sim/api.py` to get some helpful methods, particularly involving timers
- Manually work through the count-to-infinity example at the bottom of the [FAQ page](faq.md) to make sure you understand how that is supposed to work.
- Write your own tests! Don't assume that the ones we give you are exhaustive

## FAQ

See the [FAQ page](faq.md).

## Submission Details

You will be submitting your project on [okpy](http://okpy.org). When you visit the webpage, sign in using your Berkeley email. You should already be automatically registered as a student in the course. If this is not the case or you encounter any issues, please fill out this [form](https://docs.google.com/forms/d/e/1FAIpQLSduin2CqBVKc7FjJKYBY1W5sAHxwMtnias4NkhKg6tE5qlghA/viewform).

You can then upload your project files into the "Project 2" assignment by selecting the assignment and then selecting to create a new submission. You will not be receiving any feedback from the autograder until the project is over, but you can submit as many times as you want. By default, your most recent submission will be graded. If you don't want this behavior, you can select to have a previous one graded instead.

## Changelog

Updates/changes to the project will go here

#### 18 September 2017

- Clarify in "Logistics" that the project can be completed on Windows, Linux or Mac OS X, and in either Python 2 or 3, provided that the submitted project runs on a Linux system using Python 2

#### 27 September 2017

- Change `netvis` to `NetVis` for case-sensitive filesystems
- Add notes to `simulator_guide.md` for Windows installation

## Acknowledgments

This assignment was developed by Murphy McCauley in [Fall 2011](https://inst.eecs.berkeley.edu/~ee122/fa11/).
