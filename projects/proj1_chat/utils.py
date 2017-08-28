MESSAGE_LENGTH = 200

#### Client messages ####

# Message printed when a client can't connect to the server host and port that were passed in.
CLIENT_CANNOT_CONNECT = "Unable to connect to {0}:{1}"

# Message printed before exiting, if the server disconnected.
CLIENT_SERVER_DISCONNECTED = "Server at {0}:{1} has disconnected"

# Printed at the beginning of new lines in the client.
CLIENT_MESSAGE_PREFIX = "[Me] "

# Message that can be printed over the above prefix to clear it.
# This string has white space at the end to ensure that all of the
# "[Me]" prefix is overwritten with this string. The next string written
# to stdout will need to begin with "\r" to avoid unnecessary white
# space.
CLIENT_WIPE_ME = "\r    "

#### Server messages ####

# The client sent a control message (a message starting with "/") that doesn't exist
# (e.g., /foobar).
SERVER_INVALID_CONTROL_MESSAGE = \
  "{} is not a valid control message. Valid messages are /create, /list, and /join."

# Message returned when a client attempts to join a channel that doesn't exist.
SERVER_NO_CHANNEL_EXISTS = "No channel named {0} exists. Try '/create {0}'?"

# Message sent to a client that uses the "/join" command without a channel name.
SERVER_JOIN_REQUIRES_ARGUMENT = "/join command must be followed by the name of a channel to join."

# Message sent to all clients in a channel when a new client joins.
SERVER_CLIENT_JOINED_CHANNEL = "{0} has joined"

# Message sent to all clients in a channel when a client leaves.
SERVER_CLIENT_LEFT_CHANNEL = "{0} has left"

# Message sent to a client that tries to create a channel that doesn't exist.
SERVER_CHANNEL_EXISTS = "Room {0} already exists, so cannot be created."

# Message sent to a client that uses the "/create" command without a channel name.
SERVER_CREATE_REQUIRES_ARGUMENT = \
  "/create command must be followed by the name of a channel to create"

# Message sent to a client that sends a regular message before joining any channels.
SERVER_CLIENT_NOT_IN_CHANNEL = \
  "Not currently in any channel. Must join a channel before sending messages."
