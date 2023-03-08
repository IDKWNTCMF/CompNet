from urllib.parse import urlparse


class Request:
    def __init__(self, method, target):
        self.method = method
        self.target = target
        self.path = urlparse(self.target).path