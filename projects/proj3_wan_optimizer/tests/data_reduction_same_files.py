import os
import sys

import client
import wan

def data_reduction_same_files(middlebox_module, testing_part_1):
    """ Tests that the WAN optimizer reduces data sent over the WAN.

    This test sends the same file twice, and then checks that the reduction
    ratio:
        (bytes sent from client - bytes sent over wan) / 
            bytes sent from client
    is as expected. The reduction ratios in the test are hardcoded based on
    a reference solution.
    """
    if testing_part_1:
        expected_value = 0.48
    else:
        expected_value = 0.49

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    # Send a file twice from client 1 to client 2.
    filename = "sample.txt"
    output_file_name = "{}-{}".format("client2", filename)
    client1.send_file(filename, client2_address)
    # Removing the file just created
    os.remove(output_file_name)
    client1.send_file(filename, client2_address)
    # Removing the file just created
    os.remove(output_file_name)

    # Compute the data reduction ratio
    with open(filename, "rb") as input_file:
        input_data = input_file.read()

    extra_data_length = len(filename) + len(client.FILENAME_DELIMITER)
    bytes_in_sent_file = len(input_data) + extra_data_length

    bytes_sent = wide_area_network.get_total_bytes_sent()

    # print bytes_sent, bytes_in_sent_file, bytes_in_received_file

    reduction = (float(bytes_in_sent_file * 2 - bytes_sent)
                 / float(bytes_in_sent_file * 2))

    if (reduction < expected_value):
        raise Exception("data_reduction_same_files failed," +
                        " because reduction ratio should be greater than " +
                        " {}, was {}.".format(expected_value, reduction))
