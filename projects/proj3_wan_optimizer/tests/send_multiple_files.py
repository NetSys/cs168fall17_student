import os
import sys

import client
import wan

def send_multiple_files(middlebox_module, testing_part_1):
    total_count = 0
    sent_files = 4

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize clients 1 and 2, which are connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)
    client2_address = "1.2.3.5"
    client2 = client.EndHost("client2", client2_address, middlebox1)

    # Initialize clients 3 and 4, which are connected to middlebox 2.
    client3_address = "5.6.7.8"
    client3 = client.EndHost("client3", client3_address, middlebox2)
    client4_address = "5.6.7.9"
    client4 = client.EndHost("client4", client4_address, middlebox2)

    filename = "sample.txt"
    with open(filename, "rb") as input_file:
        input_data = input_file.read()

    # Send the sample file from client 1 to both clients 3 and 4.
    client1.send_file(filename, client3_address)
    client1.send_file(filename, client4_address)

    # Make sure that the files have the same contents.
    for receiver in ["client3", "client4"]:
        output_file_name = "{}-{}".format(receiver, filename)
        with open(output_file_name, "rb") as output_file:
            result_data = output_file.read()
        # Remove the output file just created.
        os.remove(output_file_name)

        if input_data == result_data:
            total_count += 1

    # Send a file from client 2 to clients 3 and 4.
    client2.send_file(filename, client3_address)
    client2.send_file(filename, client4_address)

    # Make sure that the files have the same contents.
    for receiver in ["client3", "client4"]:
        output_file_name = "{}-{}".format(receiver, filename)
        with open(output_file_name, "rb") as output_file:
            result_data = output_file.read()
        # Removing the output file just created
        os.remove(output_file_name)

        if input_data == result_data:
            total_count += 1

    if total_count != sent_files:
        raise Exception(
            "send_mutiple_files failed, because the all files" +
            "received did not match the file sent. Files received correctly:" +
            " {} and files sent are: {}\n".format(
                total_count,
                sent_files))
