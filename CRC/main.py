import sys

from crc import *

if __name__ == '__main__':
    message = str(sys.argv[1])
    g = int(sys.argv[2])
    p = float(sys.argv[3])

    message = bytearray(message, encoding='utf-8')
    crcs = compute_CRCs(message, g)
    print('-------------------Alter----------------------')
    altered_message, expected_alters = alter_data(message, 0.3)
    print('------------------Validate--------------------')
    actual_alters = validate_CRCs(altered_message, 97, crcs)
