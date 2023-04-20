def get_checksum(bytes_, k=16):
    step = k // 8
    checksum = 0
    for i in range(0, len(bytes_), step):
        checksum += int.from_bytes(bytes_[i : i + step] + bytes([0] * (i + step - len(bytes_))), byteorder='big')
        checksum %= 2**k

    return (2**k - 1) - checksum

def val_checksum(bytes_, k=16):
    step = k // 8
    checksum = 0
    for i in range(0, len(bytes_), step):
        checksum += int.from_bytes(bytes_[i : i + step] + bytes([0] * (i + step - len(bytes_))), byteorder='big')
        checksum %= 2**k

    return checksum == 2**k - 1
