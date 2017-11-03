import simple_client
import test_utils
import wan


def verify_data_is_sent_incrementally(middlebox_module, is_testing_part1):
    """ Verifies that data is sent incrementally over the WAN.

    This test makes sure that the WAN optimizer doesn't wait for a FIN
    packet to send data over the WAN.
    """

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(
        client1_address, middlebox1, client1_output_filename)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)

    # Send exactly one block from client 1 to client 2.
    if is_testing_part1:
        single_block = "a" * 8000
    else:
        single_block = ("From the lower part of the face he appeared" +
        " to be a man of strong character, with a thick, hanging lip," +
        " and a long, straight chin suggestive of resolution pushed t")
    client1.send_data(single_block, client2_address)

    wan_bytes_sent = wide_area_network.get_total_bytes_sent()
    if wan_bytes_sent != len(single_block):
        raise Exception(
            "Since a complete block was sent to the WAN " +
            "optimizer, a complete block should have been sent over the " +
            "WAN, but only {} bytes were sent.".format(wan_bytes_sent))

    # Send a second block, and then close the stream.
    second_block = "b" * 8000
    client1.send_data(second_block, client2_address)
    client1.send_fin(client2_address)

    test_utils.verify_data_sent_equals_data_received(
        single_block + second_block, client2_output_filename)
