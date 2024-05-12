import time

class DNSObject:
    def __init__(self, ttl, name=None):
        self.name = name
        self.init_time = time.time()
        self.ttl = ttl
        self.objects = []

class Cache:
    def __init__(self):
        self.a = None
        self.aaaa = None
        self.ns = None
        self.ptr = None

    def delete_expired_records(self):
        if self.a is not None and remain_ttl(self.a) == 0:
            self.a = None
        if self.aaaa is not None and remain_ttl(self.aaaa) == 0:
            self.aaaa = None
        if self.ns is not None and remain_ttl(self.ns) == 0:
            self.ns = None
        if self.ptr is not None and remain_ttl(self.ptr) == 0:
            self.ptr = None

def remain_ttl(obj):
    passed_time = int(time.time() - obj.init_time)
    return max(0, obj.ttl - passed_time)

def save_cache(cache):
    try:
        with open('dns_cache.txt', 'w') as file:
            for name, records in cache.items():
                file.write(name + '\n')
                for record_type, data in records.items():
                    file.write(f"{record_type}:{data.name}:{data.ttl}:{','.join(data.objects)}\n")
            print("Кэш сохранен в файл dns_cache.txt")
    except Exception as e:
        print("Ошибка при сохранении кэша:", e)

def load_cache():
    cache = {}
    try:
        with open('dns_cache.txt', 'r') as file:
            lines = file.readlines()
            name = None
            for line in lines:
                line = line.strip()
                if line:
                    if ':' not in line:
                        name = line
                        cache[name] = {}
                    else:
                        record_type, name, ttl, *objects = line.split(':')
                        cache[name][record_type] = DNSObject(int(ttl), name)
                        cache[name][record_type].objects = objects
            print("Кэш загружен из файла dns_cache.txt")
    except FileNotFoundError:
        print("Файл кэша не найден")
    except Exception as e:
        print("Ошибка при загрузке кэша:", e)
    return cache
