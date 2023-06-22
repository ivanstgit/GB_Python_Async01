from ipaddress import ip_address
import os
from tabulate import tabulate
from subprocess import Popen, PIPE

# 1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
# В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().

STATUSES = {
    True: "Узел доступен",
    False: "Узел недоступен"
}


def host_ping(ip_addr: list, timeout=50, attempts=1, print_res=True) -> list:
    result = []
    sysname = os.uname()[0]
    if sysname != 'Linux':
        print(f' OS {sysname} is not supported')
        raise OSError()

    for addr in ip_addr:
        ip_result = False

        try:
            ip = ip_address(addr)
        except (ValueError):
            ip = addr

        proc = Popen([f'ping', f'{ip}',
                      '-i', f'{timeout}',
                      '-c', f'{attempts}'],
                     stdout=PIPE,
                     stderr=None,
                     shell=False
                     )

        proc.wait()

        if proc.returncode == 0:
            try:
                out = proc.stdout
                if out:
                    # 1 packets transmitted, 1 received, 0% packet loss, time 0ms
                    line = out.readlines()[-2].decode()
                    received = int(line.split(sep=", ")[1].split()[0])
                    if received > 0:
                        ip_result = True
            except Exception:
                pass
        if print_res:
            print(f'ping {addr}: {STATUSES.get(ip_result)}')
        result.append(ip_result)

    return result


# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
# Меняться должен только последний октет каждого адреса.
# По результатам проверки должно выводиться соответствующее сообщение.
def host_range_ping(ip_addr_from: str, scan_cnt: int, print_res=True):
    mask = '.'.join(ip_addr_from.split('.')[0:3])
    start_byte = int(ip_addr_from.split('.')[3])
    end_byte = min(255, start_byte + scan_cnt)
    ip_addr = list(['.'.join([mask, str(byte)])
                    for byte in range(start_byte, end_byte)])
    return list(zip(ip_addr, host_ping(ip_addr, print_res=print_res)))

# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
# Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в
# табличном формате (использовать модуль tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:


def host_range_ping_tab(ip_addr_from: str, scan_cnt: int):

    res_all = host_range_ping(ip_addr_from, scan_cnt, False)
    res = {
        'Reachable': '\n'.join([r[0] for r in res_all if r[1]]),
        'Unreachable': '\n'.join([r[0] for r in res_all if not r[1]])
    }
    print(tabulate([res], headers='keys', tablefmt="pipe", stralign="left"))


if __name__ == '__main__':
    arr = ['192.168.0.1', '192.168.1.1', '192.168.100.1', 'ya.ru']

    print('Task 1')
    host_ping(arr)
# ping 192.168.0.1: Узел доступен
# ping 192.168.1.1: Узел недоступен
# ping 192.168.100.1: Узел недоступен
# ping ya.ru: Узел доступен
    print('Task 2')
    host_range_ping('192.168.0.1', 10)
# ping 192.168.1: Узел доступен
# ping 192.168.2: Узел недоступен
# ping 192.168.3: Узел недоступен
# ping 192.168.4: Узел недоступен
# ping 192.168.5: Узел недоступен
# ping 192.168.6: Узел недоступен
# ping 192.168.7: Узел недоступен
# ping 192.168.8: Узел недоступен
# ping 192.168.9: Узел недоступен
# ping 192.168.10: Узел недоступен
    print('Task 3')
    host_range_ping_tab('192.168.0.1', 10)
# | Reachable   | Unreachable   |
# |:------------|:--------------|
# | 192.168.0.1 | 192.168.0.2   |
# |             | 192.168.0.3   |
# |             | 192.168.0.4   |
# |             | 192.168.0.5   |
# |             | 192.168.0.6   |
# |             | 192.168.0.7   |
# |             | 192.168.0.8   |
# |             | 192.168.0.9   |
# |             | 192.168.0.10  |
