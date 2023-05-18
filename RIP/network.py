class Network:
    def __init__(self, routers):
        self.routers = routers

    def rip(self):
        for router in self.routers.values():
            print(f'Start state of router {router.ip} table:')
            router.print_tables(self.routers)
        print()
        step = 1
        while True:
            updated = False
            for router in self.routers.values():
                router.send_tables(self.routers)
            for v, router in self.routers.items():
                router_updated = router.process_updates()
                updated = updated | router_updated
            for router in self.routers.values():
                print(f'Simulation step {step} of router {router.ip} table:')
                router.print_tables(self.routers)
            print()
            if not updated:
                break
            step += 1
        for router in self.routers.values():
            print(f'Final state of router {router.ip} table:')
            router.print_tables(self.routers)