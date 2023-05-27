import unittest
import numpy as np
from crc import *


def compute_CRCs(data, g):
    crcs = []
    for i in range(0, len(data), 5):
        packet = data[i : i + 5]
        print(f'Packet {i // 5}')
        crc = compute_crc(packet, g)
        crcs.append(crc)
        print('---------------------------------------------')
    return crcs

def alter_data(data, p):
    alters = 0
    for i in range(0, len(data), 5):
        if np.random.binomial(1, p, 1)[0] == 1:
            idx = i + np.random.choice(len(data[i : i + 5]), 1)[0]
            el = data[idx] ^ (2**np.random.randint(0, 7))
            if el != data[idx]:
                old_decoded = data[i : i + 5].decode('utf-8')
                data[idx] = el
                alters += 1
                new_decoded = data[i : i + 5].decode('utf-8')
                print(f'Packet {i // 5} has been altered ({old_decoded} -> {new_decoded})')
    return data, alters

def validate_CRCs(data, g, crcs):
    alters = 0
    for i in range(0, len(data), 5):
        packet = data[i : i + 5]
        decoded = packet.decode('utf-8')
        if validate_data_with_crc(packet, crcs[i // 5], g):
            print(f'Packet {i // 5} is correct!')
        else:
            print(f'Packet {i // 5} cannot be verified with CRC {crcs[i // 5]:b}! (Data: {decoded})')
            alters += 1
    return alters

class CRCTestCase(unittest.TestCase):
    def test_simple(self):
        print('\n---------------Test simple------------------')
        bytes_ = bytearray('simple', encoding='utf-8')
        crcs = compute_CRCs(bytes_, 97)
        print('------------------Validate--------------------')
        alters = validate_CRCs(bytes_, 97, crcs)
        self.assertTrue(alters == 0)

    def test_with_alters(self):
        print('\n-------------Test with alters---------------')
        bytes_ = bytearray('Hello, world!', encoding='utf-8')
        crcs = compute_CRCs(bytes_, 97)
        print('-------------------Alter----------------------')
        bytes_, expected_alters = alter_data(bytes_, 0.3)
        print('------------------Validate--------------------')
        actual_alters = validate_CRCs(bytes_, 97, crcs)
        self.assertTrue(expected_alters == actual_alters)