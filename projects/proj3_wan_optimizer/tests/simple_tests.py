import simple_client
import tcp_packet
import test_utils
import utils
import wan

def simple_send_test(middlebox_module, data_to_send, data_to_send_in_reverse):
    """ Sends data between two clients.

    Verifies that the data received equals the data sent, and throw an Exception
    if this is not the case.
    """
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(client1_address, middlebox1, client1_output_filename)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(client2_address, middlebox2, client2_output_filename)

    if data_to_send:
        client1.send_data(data_to_send, client2_address)
        client1.send_fin(client2_address)
        # Verify that the correct data was received.
        if not client2.received_fin:
            raise Exception("Client 2 never received a fin")
        test_utils.verify_data_sent_equals_data_received(
            data_to_send,
            client2_output_filename)

    if data_to_send_in_reverse:
        client2.send_data(data_to_send_in_reverse, client1_address)
        client2.send_fin(client1_address)
        if not client1.received_fin:
            raise Exception("Client 1 never received a fin")
        test_utils.verify_data_sent_equals_data_received(
            data_to_send_in_reverse,
            client1_output_filename)

def send_less_than_one_block(middlebox_module, testing_part_1):
    """ Sends the payload "small data" from one client to another.
    
    Verifies that the receiving client received the correct data. This
    test only checks for correctness, and does not check the WAN optimizer's
    data reduction functionality.
    """
    simple_send_test(middlebox_module, "small data", None)

def send_exactly_one_block(middlebox_module, testing_part_1):
    """ Sends exactly one block (8000 bytes) from one client to another.
    
    Verifies that the receiving client received the correct data. This
    test only checks for correctness, and does not check the WAN optimizer's
    data reduction functionality.
    """ 
    one_block = "a" * 8000
    simple_send_test(middlebox_module, one_block, None)

def send_exactly_one_block_both_directions(middlebox_module, testing_part_1):
    """ Sends exactly one block (8000 bytes) in both directions between two clients.

    This test first sends 8000 bytes from one client to another, and then sends 8000
    bytes in the reverse direction.
 
    Verifies that the receiving client received the correct data. This
    test only checks for correctness, and does not check the WAN optimizer's
    data reduction functionality.
    """   
    first_block = "1" * 8000
    second_block = "2" * 8000
    simple_send_test(middlebox_module, first_block, second_block)

def send_multiple_different_blocks(middlebox_module, testing_part_1):
    """ Sends 20K bytes (a little more than 2 blocks) from one client to another.

    The blocks in this test are different from each other.

    Verifies that the receiving client received the correct data. This test only
    checks for crrectness, and does not check the WAN optimizer's data reduction
    functionality.
    """
    if testing_part_1:
        data = "a" * 5000 + "b" * 5000 + "c" * 5000 + "d" * 5000
    else:
        # The last character in the first block should be the "t" in "to". The remaining
        # text should be a second block.
        data = "a long, straight chin suggestive of resolution pushed to the length of obstinacy"
    simple_send_test(middlebox_module, data, None)


def one_client_with_multiple_receivers(middlebox_module, testing_part_1):
    """ Tests a scenario where one client is sending data to 3 other clients.

    Verifies that the data received equals the data sent, and throw an Exception
    if this is not the case.
    """
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(client1_address, middlebox1, client1_output_filename)

    # Initialize 3 clients connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(
        client2_address, middlebox2, client2_output_filename)

    client3_address = "5.6.7.9"
    client3_output_filename = "{}_output".format(client3_address)
    client3 = simple_client.SimpleClient(
        client3_address, middlebox2, client3_output_filename)

    client4_address = "5.6.7.10"
    client4_output_filename = "{}_output".format(client4_address)
    client4 = simple_client.SimpleClient(
        client4_address, middlebox2, client4_output_filename)

    # Send data from client 1 to client 2.
    data_to_client2 = "2" * 8000
    client1.send_data(data_to_client2, client2_address)
    client1.send_fin(client2_address)
    test_utils.verify_data_sent_equals_data_received(
        data_to_client2,
        client2_output_filename)

    # Send different data from client 1 to client 3.
    data_to_client3 = "3" * 8000
    client1.send_data(data_to_client3, client3_address)
    client1.send_fin(client3_address)
    test_utils.verify_data_sent_equals_data_received(
        data_to_client3, client3_output_filename)

    # And finally, send data from client 1 to client 4.
    data_to_client4 = "4" * 8000
    client1.send_data(data_to_client4, client4_address)
    client1.send_fin(client4_address)
    test_utils.verify_data_sent_equals_data_received(
        data_to_client4, client4_output_filename)


