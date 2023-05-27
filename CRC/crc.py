import numpy as np

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