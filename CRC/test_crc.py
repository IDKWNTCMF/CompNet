import unittest
from crc import *

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