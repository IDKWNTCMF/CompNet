def compute_crc(data, g):
    decoded = data.decode('utf-8')
    encoded = int.from_bytes(data, byteorder='big')
    print(f'Data: {decoded}')
    pw = 0
    while 2**pw < g:
        pw += 1
    data = int.from_bytes(data, byteorder='big') * 2**(pw - 1)
    crc = (g - data % g) % g
    print(f'Encoded: {encoded:b}, CRC: {crc:b}, g: {g:b}')
    return crc


def validate_data_with_crc(data, crc, g):
    pw = 0
    while 2**pw < g:
        pw += 1
    data = int.from_bytes(data, byteorder='big') * 2**(pw - 1)
    data += crc
    return data % g == 0