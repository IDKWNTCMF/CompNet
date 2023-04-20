import unittest

from StopAndWait.Checksum.checksum import get_checksum, val_checksum


class ChecksumTestCase(unittest.TestCase):
    def test_simple(self):
        bytes_ = bytes('simple', encoding='utf-8')
        checksum = get_checksum(bytes_)
        bytes_ = checksum.to_bytes(2, byteorder='big') + bytes_
        self.assertTrue(val_checksum(bytes_))

    def test_checksum_on_different_data(self):
        bytes_ = bytes('correct', encoding='utf-8')
        checksum = get_checksum(bytes_)
        bytes_ = checksum.to_bytes(2, byteorder='big') + bytes('wrong', encoding='utf-8')
        self.assertFalse(val_checksum(bytes_))

    def test_correct_checksum_on_different_data(self):
        bytes_ = bytes([1, 1, 2, 3, 5, 8, 13])
        checksum = get_checksum(bytes_)
        bytes_ = checksum.to_bytes(2, byteorder='big') + bytes([129, 1, 130, 3, 133, 8, 141])
        self.assertTrue(val_checksum(bytes_))


if __name__ == '__main__':
    unittest.main()
