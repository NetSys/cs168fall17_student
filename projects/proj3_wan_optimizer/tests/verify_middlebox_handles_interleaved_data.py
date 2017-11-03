import simple_client
import test_utils
import wan

def verify_middlebox_handles_interleaved_data(middlebox_module,
                                              is_testing_part1):
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(
        client1_address, middlebox1, client1_output_filename)

    # Initialize 2 clients connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)

    client3_address = "5.6.7.9"
    client3_output_filename = "{}_output".format(client3_address)
    client3 = simple_client.SimpleClient(
        client3_address, middlebox2, client3_output_filename)

    # Send part of a block from client 1 to client 2.
    first_client2_block = "a" * 3000
    client1.send_data(first_client2_block, client2_address)

    # Now send part of a block from client 1 to client 3.
    first_client3_block = "b" * 7000
    client1.send_data(first_client3_block, client3_address)

    # Now send some more data to client 2.
    second_client2_block = "a" * 14000
    client1.send_data(second_client2_block, client2_address)

    # Send more data to client 3 and close that stream.
    second_client3_block = "b" * 9000
    client1.send_data(second_client3_block, client3_address)
    client1.send_fin(client3_address)

    if not client3.received_fin:
        raise Exception("Client 3 didn't receive the fin")

    # Close the client 2 stream.
    client1.send_fin(client2_address)
    if not client2.received_fin:
        raise Exception("Client 2 didnt't receive the fin")

    # Make sure the data is correct.
    test_utils.verify_data_sent_equals_data_received(
        first_client2_block + second_client2_block, client2_output_filename)
    test_utils.verify_data_sent_equals_data_received(
        first_client3_block + second_client3_block, client3_output_filename)
