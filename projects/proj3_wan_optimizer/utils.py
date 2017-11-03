import hashlib

MAX_PACKET_SIZE = 1500

def get_hash(data):
    """ Returns the hash of the given data. """
    hasher = hashlib.sha1()
    hasher.update(data)
    return hasher.digest()

def get_last_n_bits(string, n):
    """ Returns n lower order bits of a string. """

    """ If the string is shorter than n in bits,
        it will return the full binary representation"""
    # convert to the binary value of string1 in str format
    # 01 pads the bytes with 0s to make them of consistent length
    # reading the array from 2: removes the 0b padding with the byte
    string_in_bits = ''.join([format(char, '#010b')[2:]
                                  for char in bytearray(string)])
    # get the last n bits of the binary string1
    last_n_bits_of_hash = string_in_bits[-n:]
    return last_n_bits_of_hash

