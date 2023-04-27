import netifaces


if __name__ == '__main__':
    for interface in netifaces.interfaces():
        print(f'Interface: {interface}')
        addresses = netifaces.ifaddresses(interface)[netifaces.AF_INET]
        for addr in addresses:
            ip = addr['addr']
            netmask = addr['netmask']
            print(f'IP: {ip}, Netmask: {netmask}')
