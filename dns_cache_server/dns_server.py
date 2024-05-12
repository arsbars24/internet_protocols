import socket
import dnslib
import threading
from cache import *

LOCK = threading.Lock()

def check_exit(DNS_server):
    while not DNS_server.is_exit:
        inp = input()
        if inp == 'exit':
            DNS_server.is_exit = True

class DNSServer:
    def __init__(self, cache):
        self.cache = cache
        self.is_exit = False

    def start(self, HOST, DNS_PORT, DNS_SERVER):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as remote_server_socket:
                server_sock.bind((HOST, DNS_PORT))
                remote_server_socket.connect((DNS_SERVER, DNS_PORT))
                server_sock.settimeout(1.0)
                remote_server_socket.settimeout(1.0)
                while not self.is_exit:
                    try:
                        query_data, customer_addr = server_sock.recvfrom(10000)
                        parser_query = dnslib.DNSRecord.parse(query_data)
                        with LOCK:
                            cache_records = self.cache.get(parser_query.q.qname.label)
                            if cache_records is not None:
                                cache_records.delete_expired_records()
                                required_info = get_required_info(cache_records, parser_query)
                                if required_info is not None:
                                    print('Данные взяты из КЭШа')
                                    self.add_answer_to_query(required_info, parser_query)
                                    server_sock.sendto(parser_query.pack(), customer_addr)
                                    continue
                            print('Идёт обращение к старшему ДНС серверу')
                            remote_server_socket.send(query_data)
                            respond_data, _ = remote_server_socket.recvfrom(10000)
                            server_sock.sendto(respond_data, customer_addr)
                            parsed_respond = dnslib.DNSRecord.parse(respond_data)
                            update_cache_records(parsed_respond, self.cache)
                    except socket.timeout:
                        pass
                    except Exception as e:
                        print(e)

    @staticmethod
    def add_answer_to_query(required_data, query):
        q_type = query.q.qtype
        q = query.q
        if q_type == dnslib.QTYPE.A:
            for addr in required_data.objects:
                query.add_answer(dnslib.RR(q.qname, q.qclass, q.qtype, remain_ttl(required_data), dnslib.A(addr)))
        if q_type == dnslib.QTYPE.AAAA:
            for addr in required_data.objects:
                query.add_answer(dnslib.RR(q.qname, q.qclass, q.qtype, remain_ttl(required_data), dnslib.AAAA(addr)))
        if q_type == dnslib.QTYPE.NS:
            for addr in required_data.objects:
                query.add_answer(dnslib.RR(q.qname, q.qclass, q.qtype, remain_ttl(required_data), dnslib.NS(addr)))
        if q_type == dnslib.QTYPE.PTR:
            query.add_answer(dnslib.RR(q.qname, q.qclass, q.qtype, remain_ttl(required_data), dnslib.PTR(required_data.name)))

def update_cache_records(dns_answer, cache):
    for new_record in dns_answer.rr + dns_answer.ar + dns_answer.auth:
        record_type = new_record.rtype
        name = new_record.rname.label
        cache_records = cache[name]
        if record_type == dnslib.QTYPE.NS:
            update_ns(new_record, cache_records)
        elif record_type == dnslib.QTYPE.A:
            update_a(new_record, cache_records)
        elif record_type == dnslib.QTYPE.AAAA:
            update_aaaa(new_record, cache_records)
        elif record_type == dnslib.QTYPE.PTR:
            update_ptr(new_record, cache_records)

def update_ns(new_record, cached_records):
    if cached_records.ns is None:
        cached_records.ns = DNSObject(new_record.ttl)
    cached_records.ns.objects.append(new_record.rdata.label.label)

def update_a(new_record, cached_records):
    if cached_records.a is None:
        cached_records.a = DNSObject(new_record.ttl)
    cached_records.a.objects.append(new_record.rdata.data)

def update_aaaa(new_record, cached_records):
    if cached_records.aaaa is None:
        cached_records.aaaa = DNSObject(new_record.ttl)
    cached_records.aaaa.objects.append(new_record.rdata.data)

def update_ptr(new_record, cached_records):
    if cached_records.ptr is None:
        cached_records.ptr = DNSObject(new_record.ttl, new_record.rdata.label.label)

def get_required_info(cache_records, query):
    q_type = query.q.qtype
    if q_type == dnslib.QTYPE.A:
        return cache_records.a
    elif q_type == dnslib.QTYPE.AAAA:
        return cache_records.aaaa
    elif q_type == dnslib.QTYPE.NS:
        return cache_records.ns
    elif q_type == dnslib.QTYPE.PTR:
        return cache_records.ptr
