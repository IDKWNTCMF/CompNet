import json
import sys

from network import Network
from router import Router


def validate_unique_ips(routers_):
    return len(routers_) == len(set(map(lambda router_: router_.ip, routers_)))

if __name__ == '__main__':
    config_path = sys.argv[1]
    config = json.load(open(config_path))
    routers = dict()
    for v, info in config.items():
        routers[int(v)] = Router(v, info)
    if not validate_unique_ips(routers.values()):
        print('IPs are not unique!')
        exit(-1)
    network = Network(routers)
    network.rip()