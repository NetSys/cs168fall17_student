def verify_data_sent_equals_data_received(data_sent, output_filename):
    with open(output_filename, "rb") as f:
        received_data = f.read()
        if received_data != data_sent:
            raise Exception(("Data received did not equal " +
                "data sent. Data sent:\n{}\nData " +
                "received:\n{}\n").format(data_sent, received_data))


