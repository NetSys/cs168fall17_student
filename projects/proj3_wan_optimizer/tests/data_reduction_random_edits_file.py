import os
import sys

import client
import wan

def data_reduction_random_edits_file(middlebox_module, testing_part_1):
    """ Tests that the WAN optimizer reduces data sent over the WAN.

    This test sends a file and then sends the same file with some random
    edits in the contents of the file. This will result in no reduction of
    data sent over the wan for the part 1 middlebox, but the version for part
    2 should still achieve significant data reduction.  The test checks that
    the reduction ratio:
        (bytes sent from client - bytes sent over wan) / 
            bytes sent from client
    is as expected. The reduction ratios in the test are hardcoded based on
    a reference solution.
    """  
    if testing_part_1:
        expected_value = 0.0
    else:
        expected_value = 0.38

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    filename = ["random_sample1.txt", "random_sample2.txt"]

    # Send a file from client 1 to client 2.
    client1.send_file(filename[0], client2_address)
    output_file_name = "{}-{}".format("client2", filename[0])
    # Removing the output file just created
    os.remove(output_file_name)
    # Send a file prefixed with some data in the beginning
    # of the same file
    client1.send_file(filename[1], client2_address)
    output_file_name = "{}-{}".format("client2", filename[1])
    # Remove the output file just created
    os.remove(output_file_name)

    bytes_in_sent_files = 0
    for f in filename:
        with open(f, "rb") as input_file:
            input_data = input_file.read()

        extra_data_length = len(f) + len(client.FILENAME_DELIMITER)
        bytes_in_sent_files += len(input_data) + extra_data_length

    bytes_sent = wide_area_network.get_total_bytes_sent()

    reduction = (float(bytes_in_sent_files - bytes_sent)
                 / float(bytes_in_sent_files))

    if (reduction < expected_value):
        raise Exception("data_reduction_random_edit_file failed," +
                        " because reduciton ratio should be greater than " +
                        " {}, was {}.".format(expected_value, reduction))
