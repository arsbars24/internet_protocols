import time

class DNSCache:
    def __init__(self):
        self.domain_to_ip = {}
        self.ip_to_domain = {}
        self.expiry_times = {}

    def add(self, query_name, ip_address, ttl):
        expiry_time = time.time() + ttl
        self.domain_to_ip[query_name] = (ip_address, expiry_time)
        self.ip_to_domain[ip_address] = (query_name, expiry_time)

    def get(self, query_name):
        current_time = time.time()
        if query_name in self.domain_to_ip:
            ip, expiry_time = self.domain_to_ip[query_name]
            if expiry_time > current_time:
                return ip
        return None

    def remove_expired_records(self):
        current_time = time.time()
        self.domain_to_ip = {k: v for k, v in self.domain_to_ip.items() if v[1] > current_time}
        self.ip_to_domain = {k: v for k, v in self.ip_to_domain.items() if v[1] > current_time}
