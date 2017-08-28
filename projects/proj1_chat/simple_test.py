""" A simple test that verifies that messages between two clients are received. """

import select
import sys
import time
from subprocess import Popen, PIPE

SLEEP_SECONDS = 0.1 

class SimpleTest():
    def run(self, port):
        self.setup(port)
        try:
          self.test_two_clients()
        finally:
          self.tear_down()

    def setup(self, port, host="localhost"):
        """Sets up a server and four clients."""
        self.server = Popen(["python", "server.py", str(port)])
        # Give the server time to come up.
        time.sleep(SLEEP_SECONDS)

        self.alice_client = Popen(["python", "client.py", "Alice", host, str(port)], stdin=PIPE, stdout=PIPE)
        self.kay_client = Popen(["python", "client.py", "Kay", host, str(port)], stdin=PIPE, stdout=PIPE)
        time.sleep(SLEEP_SECONDS)

    def tear_down(self):
        """ Stops the clients and server. """
        self.alice_client.kill()
        self.kay_client.kill()
        self.server.kill()

    def get_message_from_buffer(self, buf):
        """Strips all formatting, including [Me] and whitespace."""
        s =  "".join(buf).replace('[Me]', '').strip()
        return s

    def check_for_output(self, client, expected_output, check_formatting=False):
        """ Verifies that the given client's stdout matches the given output."""
        output_buffer = []
        end_time = time.time() + 1
        # Read one character at a time from stdout until either time timeout expires, or
        # the output is correct.
        while (self.get_message_from_buffer(output_buffer) != expected_output
                and time.time() < end_time):
            select_timeout = end_time - time.time()
            ready_to_read, ready_to_write, in_error = select.select(
                [client.stdout], [], [], select_timeout)
            for readable_socket in ready_to_read:
                char = readable_socket.read(1)
                output_buffer.append(char)

        message = self.get_message_from_buffer(output_buffer)
        if message != expected_output:
            raise Exception("Client output:\n{}; expected:\n{}".format(
                repr(message), repr(expected_output)))

    def test_two_clients(self):
        self.alice_client.stdin.write("/create tas\n")
        # Sleep to make sure that the message from Alice, to create the tas channel,
        # arrives at the server before Kay's message to join the channel.
        time.sleep(SLEEP_SECONDS)
        self.kay_client.stdin.write("/join tas\n")
        # Alice should get a message that Kay joined.
        self.check_for_output(self.alice_client, "Kay has joined")

        # When Kay sends a message, Alice should receive it.
        self.kay_client.stdin.write("Hi!\n")
        self.check_for_output(self.alice_client, "[Kay] Hi!")

        # When Alice sends a message, Kay should receive it.
        self.alice_client.stdin.write("Hello!\n")
        self.check_for_output(self.kay_client, "[Alice] Hello!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python simple_test.py <port>"
        sys.exit(1)

    port = int(sys.argv[1])
    SimpleTest().run(port)

