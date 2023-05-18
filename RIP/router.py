class Router:
    def __init__(self, v, info):
        self.v  = int(v)
        self.ip = info['ip']
        self.neighbours = list(map(lambda x: int(x), info['neighbours'].split(', ')))
        self.distance_table = dict()
        self.next_hop_table = dict()
        for u in self.neighbours:
            self.distance_table[u] = 1
            self.next_hop_table[u] = u
        self.updates = []

    def send_tables(self, routers):
        for u in self.neighbours:
            routers[u].updates.append((self.distance_table, self.v))

    def process_updates(self):
        updated = False
        for dist_table, u in self.updates:
            for w, dist in dist_table.items():
                if w != self.v and dist + 1 < 15 and (w not in self.distance_table or dist + 1 < self.distance_table[w]):
                    self.distance_table[w] = dist + 1
                    self.next_hop_table[w] = u
                    updated = True
        self.updates = []
        return updated

    def print_tables(self, routers):
        print('[Source IP]          [Destination IP]     [Next Hop]           [Metric]')
        for u in self.distance_table:
            print(f'{self.ip:20} {routers[u].ip:20} {routers[self.next_hop_table[u]].ip:20} {self.distance_table[u]}')
