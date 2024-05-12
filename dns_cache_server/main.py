from dns_server import DNSServer
from cache import load_cache

def main():
    cache = load_cache()
    HOST = input("Укажите ip-адрес хоста: ")
    DNS_PORT = int(input("Укажите порт хоста: "))
    DNS_SERVER = input("Укажите ip-адрес DNS сервера: ")
    server = DNSServer(cache)
    try:
        server.start(HOST, DNS_PORT, DNS_SERVER)
    except OSError as e:
        print(f'{HOST}/{DNS_PORT} уже занят')

if __name__ == "__main__":
    main()
