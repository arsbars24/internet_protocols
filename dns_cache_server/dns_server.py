import socket
import struct
import threading
import time
import pickle


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


class DNSServer:
    def __init__(self, host='127.0.0.1', port=53, cache_file='dns_cache.pkl'):
        self.host = host
        self.port = port
        self.cache_file = cache_file
        self.cache = DNSCache()

        try:
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)
                self.cache.remove_expired_records()
        except FileNotFoundError:
            pass

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print(f"DNS сервер запущен на {self.host}:{self.port}")

        threading.Thread(target=self.cleanup_cache).start()

        while True:
            data, addr = self.sock.recvfrom(512)
            threading.Thread(target=self.handle_request, args=(data, addr)).start()

    def handle_request(self, data, addr):
        try:
            query_name = self.extract_query_name(data)
            print(f"Получен запрос для {query_name} от {addr}")
            response = self.cache.get(query_name)

            if response:
                print(f"Кэш хитом для {query_name}")
                self.sock.sendto(self.build_response(data, response), addr)
            else:
                print(f"Кэш промахом для {query_name}")
                response = self.forward_request(data)
                self.sock.sendto(response, addr)
                self.cache_response(query_name, response)
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")

    def extract_query_name(self, data):
        qname = []
        idx = 12
        while True:
            length = data[idx]
            if length == 0:
                break
            qname.append(data[idx + 1:idx + 1 + length].decode())
            idx += length + 1
        return '.'.join(qname)

    def forward_request(self, data):
        upstream_server = ('8.8.8.8', 53)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, upstream_server)
        response, _ = sock.recvfrom(512)
        return response

    def cache_response(self, query_name, response):
        transaction_id = struct.unpack('!H', response[:2])[0]
        flags = struct.unpack('!H', response[2:4])[0]
        qdcount = struct.unpack('!H', response[4:6])[0]
        ancount = struct.unpack('!H', response[6:8])[0]

        if ancount == 0:
            return

        idx = 12
        while response[idx] != 0:
            idx += 1
        idx += 5

        for _ in range(ancount):
            idx += 2
            rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', response[idx:idx + 10])
            idx += 10
            rdata = response[idx:idx + rdlength]
            idx += rdlength

            if rtype == 1:  # A запись
                ip_address = socket.inet_ntoa(rdata)
                self.cache.add(query_name, ip_address, ttl)

    def build_response(self, query, ip):
        transaction_id = query[:2]
        flags = struct.pack('!H', 0x8180)
        qdcount = struct.pack('!H', 1)
        ancount = struct.pack('!H', 1)
        nscount = struct.pack('!H', 0)
        arcount = struct.pack('!H', 0)

        query_section = query[12:]
        name = query_section[:len(query_section) - 4]
        rtype = struct.pack('!H', 1)
        rclass = struct.pack('!H', 1)
        ttl = struct.pack('!I', 300)
        rdlength = struct.pack('!H', 4)
        rdata = socket.inet_aton(ip)

        response = (transaction_id + flags + qdcount + ancount + nscount + arcount +
                    query_section + name + rtype + rclass + ttl + rdlength + rdata)
        return response

    def cleanup_cache(self):
        while True:
            time.sleep(60)
            self.cache.remove_expired_records()

    def shutdown(self):
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
        self.sock.close()


if __name__ == '__main__':
    server = DNSServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()
