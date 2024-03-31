import subprocess
import re
import json
from urllib import request
from prettytable import PrettyTable

def trace_autonomous_system(target):
    tracert_proc = subprocess.Popen(["tracert", target], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    number = 0
    table = PrettyTable()
    table.field_names = ["number", "ip", "country", "AS number", "provider"]

    for raw_line in iter(tracert_proc.stdout.readline, b''):
        line = raw_line.decode('cp866')
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)

        if 'Trace complete' in line or 'Трассировка завершена' in line:
            print(table)
            return
        if 'Unable to resolve' in line or 'Не удается разрешить' in line:
            print('Invalid input')
            return
        if 'Tracing route' in line or 'Трассировка маршрута' in line:
            print(line)
            continue
        if 'Request timed out' in line or 'Превышен интервал ожидания' in line:
            print('Request timed out')
            continue
        if ip:
            number += 1
            print("".join(ip))
            info = json.loads(request.urlopen('https://ipinfo.io/' + ip[0] + '/json').read())
            if 'bogon' in info:
                table.add_row([f"{number}.", ip[0], '*', '*', '*'])
            else:
                try:
                    as_number = info['org'].split()[0][2:]
                    provider = " ".join(info['org'].split()[1:])
                except KeyError:
                    as_number, provider = '*', '*'
                table.add_row([f"{number}.", ip[0], info['country'], as_number, provider])

if __name__ == '__main__':
    target = input('Введите адрес: ')
    trace_autonomous_system(target)
