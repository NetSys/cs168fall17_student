import os
import sys

import client
import wan

def send_image_file(middlebox_module, testing_part_1):
    """ Verifies that sending an image (as opposed to text) file works correctly. """
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
    filename = "sample.jpg"
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    with open(filename, "rb") as input_file:
        input_data = input_file.read()

    output_file_name = "{}-{}".format("client2", filename)
    with open(output_file_name, "rb") as output_file:
        result_data = output_file.read()
    # Removing the output file just created
    os.remove(output_file_name)

    if input_data != result_data:
        raise Exception("send_image_file failed, because the file received" +
                        "did not match the file sent.")
