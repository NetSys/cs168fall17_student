# Chat

In this assignment, you'll build a simple application that connects users over a network: a chat server.  Similar to chat programs like [Slack](https://www.slack.com) and [IRC](https://tools.ietf.org/html/rfc1459), your finished chat server will allow users to converse in different channels.  Users can create and join channels; once a user is in a particular channel, all messages that she sends will be relayed to all other users in that channel.

This assignment (and the rest of the assignments in this class) should be implemented in Python 2.  This assignment will introduce you to the socket programming API.

#### Logistics

- This project is due on Monday 9/11 at 11:59pm
- This project should be completed individually (refer to the [course website](http://cs168.io) for collaboration policies)
- The skeleton code for this project is available from [here](https://github.com/NetSys/cs168fall17_student/tree/master/projects/proj1_chat). You can download the code manually from that page, or use git.
- You'll submit your code using `ok`. You should submit two files: one named `client.py` and one named `server.py`. You should not modify or submit `utils.py`. More detailed submission instructions can be found in the [submission details](#submission-details) section.

#### Resources

- There's a demo of the finished project available [here](https://youtu.be/4btZs--wlpI).
- If you have questions, first take a look at the [FAQ section](#faq).  If your question isn't answered there, post to Piazza.
- The [Python Socket Programming HOWTO](https://docs.python.org/2/howto/sockets.html) is a useful introduction to socket programming.
- We've provided two files to help you test your code:
  - `client_split_messages.py` is intended to help you ensure your server is correctly buffering messages, and is described in more detail below.
  - `simple_test.py` tests a basic scenario where two clients communicate in a simple channel.  `simple_test.py` represents only a small fraction of the points that we'll test for when we grade your assignment, and is intended only to help you verify the basic format of your client's output.

## What are sockets?

A socket is an endpoint of a connection between two programs running across a network.  Each socket is associated with a particular port number.  Sockets are an abstraction provided by operating systems: programs create sockets, read from those sockets, and write to those sockets.  When a program writes to a socket, the operating system sends data out a particular port; similarly, with the operating system receives data on a port, that data can be read from the socket corresponding to that port.

In Python, you can create a socket and connect to a remote endpoint by using the [socket library](https://docs.python.org/2/library/socket.html) as follows:

    import socket
    # The socket constructor accepts a few arguments; the defaults are fine for this class.
    client_socket = socket.socket()
    client_socket.connect(("1.2.3.4", 5678))
    client_socket.sendall("Hello World")
    
The example above created a socket and connected it to port 5678 at IP address 1.2.3.4.  Then, it sent a "Hello World" message to the server at 1.2.3.4:5678.

The example above created a client socket that was connected to exactly one remote endpoint.  When you create a server, you'll typically want to allow multiple remote clients to connect, and you don't usually know the address of those clients when the socket is created.  As a result, server sockets work differently:

    server_socket = socket.socket()
    server_socket.bind(("1.2.3.4", 5678))
    server_socket.listen(5)
    
After creating the socket, rather than connecting to a particular remote destination, the code above *bound* the socket to a particular IP address and port, which essentially tells the operating system to associate the given IP address and port with the socket.  Finally, the `listen` call listens for connections made to the socket.  When a new client connects to the socket, the socket library will create a new socket to use to communicate with that client, so that the server socket can continue to be used to wait for inbound connections from other clients:

    (new_socket, address) = server_socket.accept()
    
This call blocks until a client connects (using a `connect()` call, as in the example above), and then returns a newly created socket, `new_socket`, that can be used to send and receive data to and from the client.  For example, the call

    message = new_socket.recv(1024)
    
will block until there is data to receive from the client, and will return up to 1024 bytes of data.

You'll need to do some reading to understand how all of these API calls work.  __In particular, be careful when using `send` and `recv`! `send`, for example, will not necessarily send all of the data passed into it.__  The [Python Socket Programming HOWTO](https://docs.python.org/2/howto/sockets.html) will likely be a useful resource.

## Part 0 (Optional)

The first part of the assignment will help you get started with the socket programming API and introduce you to basic client-server interaction.  __This part of the assignment is optional, will not be graded and is meant to get you familiar with sockets.__ The solution to this part will be released on Wednesday 8/30.

For this part of the assignment, you'll write a simple client and server.  The client will send a single message from stdin to the server and then disconnect.  The server should print messages it receives to stdout.  If multiple clients connect to the server, the server should handle them sequentially (i.e., it should print the complete message from one client and close that connection before handling the next client).

The server should accept one command line argument, stating the port that the server should use:

    $ python basic_server.py 12345
    
The client should accept two command line arguments: the hostname (or IP address) of the server to connect to, and the server port:

    $ python basic_client.py localhost 12345
    
Your server should be reachable from any IP address associated with the machine (see the FAQ).

### Blocking sockets

In this part of the assignment, it's fine to use blocking sockets.  "Blocking" means that a socket call may not return for a while, until the call completes.  Cases when socket calls won't complete immediately include:

- `send`: if the socket's internal buffer is full so no data can be written
- `recv`: if the internal buffer is empty, so there's no data to read (e.g., if the client has paused sending)
- `accept`: if these are no clients currently trying to connect

### Example use

Here's an example of how your client and server should work.  Suppose two different clients connected sequentially:

    $ python basic_client.py localhost 12345
    I am a student in CS168. This class is awesome!
    $ python basic_client.py localhost 12345
    Why is Shenker so bad at drawing?
    
If a server had been started on port 12345 before the client was run, it should have printed output as follows:

    $ python basic_server.py 12345
    I am a student in CS168. This class is awesome!
    Why is Shenker so bad at drawing?
 

## Part 1

In the remainder of the assignment, you'll build on your basic client and server to create a chat server with different channels that clients can communicate on.  For a demo of how your server should behave, watch the video [here](https://youtu.be/4btZs--wlpI).

### Server Functionality

The server should accept a single command line argument that's the port that the server should run on.

#### Messages

Unlike your server in part 0, your server in this part of the assignment must allow many clients to be connected and sending messages concurrently.  Each client should have an associated name (so that other connected clients know who each message is from) and channel that they're currently subscribed to.  When a client first connects, it won't have an associated name and channel.  The first message that the server receives from the client should be used as the client's name.

Future messages from the client to the server can take one of two forms.  The first type of message is a control message; control messages always begin with "/".  There are three different control messages your server should handle from clients:

- `/join <channel>` should add the client to the given channel.  Clients can only be in one channel at a time, so if the client is already in a channel, this command should remove the client from that channel. When a client is added to a channel, a message should be broadcasted to all existing members of the channel stating that the client has joined.  Similarly, if the client left a channel, a message should be broadcasted stating that the client left.
- `/create <channel>` should create a new channel with the given name, and add the client to the given channel.  As with the `/join` call, the client should be removed from any existing channels.
- `/list` should send a message back to the client with the names of all current channels, separated by newlines.

The second type of message is normal messages to the client's current channel.  All messages that are not preceeded by a `/` are considered normal messages.  These messages should be broadcasted to all other clients in the channel, preceeded by the client's name in brackets (see the example below).  Messages should _not_ be sent to client in different channels.  If the client is not currently in a channel, the server should send an error message back to the client.

When a client disconnects, a message should be broadcasted to all members of the client's channel saying that the client disconnected.

##### Delineating Messages

Sockets provide a data stream functionality, but they don't delineate different messages.  When a given `recv` call returns some data, the socket won't tell you whether the data returned is a single message, or multiple messages, or part of one message.  As a result, you'll need a way to determine when a message ends.  For this assignment, use fixed length messages that have 200 characters for all messages (including messages from the server to the client). If a message is shorter than 200 characters, you should pad the message with spaces (and the receiver should strip any spaces off of the end of the message). You can assume that no messages are longer than 200 characters.

Be sure that your code correctly handles the case where less than one message is available in the socket's buffer (so a `recv` call returns fewer than 200 characters of data) and the case where more than one message is available in the socket's buffer.  You should handle partial messages by buffering: if a `recv` call returns only part of a message, your code should hold on to the part of the message until the remainder of the mesage is received, and then handle the complete message.  For example, if a client receives 150 characters from the server, it should hold those 150 characters until 50 more characters are received.  The client should only write the message to stdout once all 200 characters have been received.  To help you check for your server's handling of these cases, we've provided a special client (`client_split_messages.py`) that splits messages into many smaller messages before sending them to the server.  This client only tests some of the scenarios your server should handle!  You'll likely want to modify this client to test for additional cases.

#### Error Handling

Your server should handle cases where the client sends an invalid message by returning an appropriate error message to the client.  For example, if a client uses the `/join` command but doesn't provide the name of a channel to join, the server should send back an error message.  The provided `utils.py` includes format strings for all of the errors you should handle.  You can use these format strings using Python's string formatting operations.  For example, `utils.py` defines the following error message:

    CLIENT_SERVER_DISCONNECTED = "Server at {0}:{1} has disconnected"
    
You can use the `.format` function to replace the brackets with strings as follows:

    error_message = CLIENT_SERVER_DISCONNECTED.format("localhost", 12345)

__You are required to use the error messages defined as constants in `utils.py`.  If you do not use the constants defined in `utils.py` , you will not get credit for error handling.__

When commands lead to an error, the command should not cause any changes at the server.  For example, if a client is currently in the `cs168_tas` channel and then tries to join a channel that doesn't exist, the client should __not__ be removed from the `cs168_tas` channel.

We will only test for errors that have associated error messages in `utils.py` in our testing.  You're welcome to check for additional errors if you'd like, but you will not be graded on them.

### Client Functionality

Each client connects to a particular chat server, and is associated with a name.  Your client should be started as follows:

    $ python client.py Scott 127.0.0.1 55555
    
This command should connect to the server at the given address and port number, and then send a message with the name Scott.

After being started, the client should listen for messages from the server and from stdin.  Messages from the server should be printed to the command line (after being stripped of any spaces at the end) and messages from stdin should be sent to the server (after being padded with spaces, as needed).  The client code should print [Me] before each message sent by that particular client so that the client can differentiate its own messages from messages sent by others.  When the client gets a message from the server, it should write over the `[Me]` with the message from the server.  For an example of this, take a look at the demo video linked above.

Here's an example of a client's interaction with a server that was started locally on port 55555:

	python client.py Panda localhost 55555
	[Me] Hello world!
	Not currently in any channel. Must join a channel before sending messages.
	[Me] /list
	[Me] /create 168_tas
	[Me] /list
	168_tas
	[Me] Hello world!
	Alice has joined
	[Alice] Hi everyone! Does anyone know what we're doing on the first day of lecture?
	
After seeing Alice's message, Panda stopped his client. After Panda created the 168_tas channel, a second client started:

	python client.py Alice 127.0.0.1 55555
	[Me] /list
	168_tas
	[Me] /join 168_tas
	[Me] Hi everyone! Does anyone know what we're doing on the first day of lecture?
	Panda has left

### Details

We've provided a `utils.py` file that has error messages that you should use.  These are intended to make your life easier, and also to enable testing.  Be sure you use these messages; otherwise, your code will fail the tests!

### Non-blocking sockets

You'll need to use non-blocking sockets for this part of the assignment, because both your client and server need to receive data from multiple sources, in an unknown order.  Consider what would happen if your client used blocking sockets, as in part 0, with a call like:

    message_from_server = client_socket.recv(200)
    
Now suppose that the server doesn't send any messages for a while, but while the client is blocked waiting on the `recv` call to return, the user types some data into stdin.  The client should read the data from stdin and send it to the server -- but the client is stuck blocked waiting on data from the server socket!  To address this problem, you can use non-blocking sockets.

To use non-blocking sockets, you'll need to use the `select` call in the `select` library.  For more about how to use `select` and a very relevant example, take a look at [this page](http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php).  While you are required to use non-blocking sockets for reading data and accepting connections, it's fine to use blocking sockets for sending messages (since the messages you're sending are short and you don't need to handle sending a large number of messages in quick succession, `send` and `sendall` should not block for long periods of time).

## Submission Details

You will be submitting your project on [okpy](http://okpy.org). When you visit the webpage, sign in using your preferred email from bCourses (Unless you have changed it, this should default to your Berkeley email). You should already be automatically registered as a student in the course. If this is not the case or you encounter any issues, please fill out this [form](https://goo.gl/forms/JdFQkp933jHH3kJm1).

You can then upload your project files into the "Project 1" assignment by selecting the assignment and then selecting to create a new submission. You will not be receiving any feedback from the autograder until the project is over, but you can submit as many times as you want. By default, your most recent submission will be graded. If you don't want this behavior, you can select to have a previous one graded instead.

## FAQ

##### What python libraries can I use?

Our solution code imports select, socket, and sys.  You should not import any other python libraries without asking first on Piazza.

##### How do I figure out the IP address to use to connect to my chat server?

If you started a server locally, your client can access the server using "localhost" or 127.0.0.1.  These are special names / addresses that are always used to refer to the local machine.  localhost and 127.0.0.1 cannot be used if you're trying to connect to your server from a different machine, because if a different machine uses those addresses, they refer to the local interface on that machine.  If you'd like to access your chat server from another machine, you'll need to determine your machine's externally reachable IP address.  There are some websites that will do this (e.g., Google "What's my IP address"), or you can also do this by running the `ifconfig` command.  `ifconfig` will list all the local interfaces; e.g.:

    $ ifconfig
    lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
	options=3<RXCSUM,TXCSUM>
		inet6 ::1 prefixlen 128 
		inet 127.0.0.1 netmask 0xff000000 
		inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
		nd6 options=1<PERFORMNUD>
	en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
		ether 78:31:c1:c0:a7:44 
		inet6 fe80::7a31:c1ff:fec0:a744%en0 prefixlen 64 scopeid 0x4 
		inet 172.19.131.124 netmask 0xffffff00 broadcast 172.19.131.255
		nd6 options=1<PERFORMNUD>
		media: autoselect
		status: active
	en1: flags=963<UP,BROADCAST,SMART,RUNNING,PROMISC,SIMPLEX> mtu 1500
		options=60<TSO4,TSO6>
		ether 72:00:02:3f:79:50 
		media: autoselect <full-duplex>
		status: inactive
		
The first entry above is the loopback address, which can be used to access the machine locally.  You'll notice the IP address of this interface (listed after `inet`) is always `127.0.0.1`.  Look for an interface listed with an IP address that's different than the loopback one -- in this example, the externally reachable IP address is `127.19.131.124` (listed under `en0`).

If you're behind a [NAT](http://en.wikipedia.org/wiki/Network_address_translation), you won't be able to reach your server from different machines.  We'll learn more about NATs later this semester.  In the meantime, if you'd like to play around with using your server from remote machines, try running it while connected to the wifi in Soda hall, which doesn't use a NAT, and assigns users unique IP addresses.

##### What's a good port number to pass in?

Many low port numbers are reserved; try using a port number greater than 10000.

##### When I start the server, I get an error that says `Address already in use`

This error means that another process is currently using the port.  Sometimes this happens transiently -- for example, if your server exited with an error, and not all of the sockets it was using have been cleaned up by the operating system yet.  When this happens, try using a different port.

##### What maximum number of connections should I use in the `listen` call?

5 is fine for this assignment.

##### Using a fixed-length message seems clunky and wasteful.  What are some alternatives?

For this assignment, you must use fixed-length messages.  If you're curious about what's used in practice, there are two common approaches.  The first is to use a delimiter between messages (e.g., some unique sequence of characters that's unlikely to be seen in any messages, such as `:==`) that can be used to determine when a message has ended.  The second (and more common) option is for the first thing in any message to be the size of the message.

##### How can I write over the "[Me]" on stdout when I get a message from the server?

You can start writing at the beginning of the current line of stdout by using "\r" at the beginning of the message you output.  One thing to be careful about is messages from the server that are shorter than the length of the "[Me]" string. For example, suppose the client sends the `/list` command to the server, and one of the channels is named "A".   The output should look like:

    [Me] /list
    A

But if you're not careful, you'll end up with output that looks like:

    [Me] /list
    AMe]
    
Use `utils.CLIENT_WIPE_ME` to fix this issue (note that if you use this constant, you'll need a "\r" at the beginning of the next string printed to avoid extra whitespace).

##### Do I ever need to close the server socket?

No. It's fine if your server code is inside of a `while True:` loop, like the server in Part 0.

##### Should the client quit if the server disconnects?

Yes.  The client should quit and print the appropriate error message from `utils.py`.

##### How will our code be tested?

We'll do end-to-end tests using your client and server together, and we'll also do tests where we use our own client to interact with your server (and vice versa).  As a result, you should make sure that your client and server communicate as described in this document.

 ##### I'm running Windows and select isn't working.
  
Unfortunately, stdin does not count as a socket in Windows due to how file descriptors work differently. Since the tests will be run on a Linux machine, this will cause issues if you write the code to use the Windows version of file descriptors. Your options are to download a Linux virtual machine, or use the instructional servers through SSH, or use the lab machines to test your code. Side note: If you are using Windows 10, you can use the Linux subsystem for Windows and run your code from there and it may work.

### Acknowledgments

This assignment was inspired by the [Introduction to Socket Programming Assignment](http://www.cs.princeton.edu/courses/archive/spr15/cos461/assignments/0-sockets.html) in Princeton's Computer Networking course.
