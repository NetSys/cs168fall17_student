import os
import sys

import client
import wan

def send_one_file(middlebox_module, testing_part_1):
    """ Sends a single large file and verifies that it's received correctly.

    This test only verifies that the correct data is received, and does not
    check the optimizer's data compression.
    """
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    # Send a file from client 1 to client 2.
    filename = "sample.txt"
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    with open(filename, "rb") as input_file:
        input_data = input_file.read()

    output_file_name = "{}-{}".format("client2", filename)
    with open(output_file_name, "rb") as output_file:
        result_data = output_file.read()
    # Remove the output file just created.
    os.remove(output_file_name)

    if input_data != result_data:
        raise Exception(
            "The file received did not match the file sent. File received had: " +
            "{}\n and file sent had: {}\n".format(result_data, input_data))
