import subprocess
from ipaddress import ip_address


def host_ping(hosts):
    for host in hosts:
        try:
            ip = ip_address(host)
        except ValueError:
            print(f"Узел недоступен: {host}")
            continue

        # Опция -c указывает количество пакетов для отправки
        result = subprocess.run(['ping', '-c', '3', str(ip)], stdout=subprocess.DEVNULL)

        if result.returncode == 0:
            print(f"Узел {ip} доступен")
        else:
            print(f"Узел {ip} недоступен")


if __name__ == '__main__':
    ip_addresses = ['yandex.ru', '2.2.2.2', '192.168.0.100', '192.168.0.101']
    host_ping(ip_addresses)
