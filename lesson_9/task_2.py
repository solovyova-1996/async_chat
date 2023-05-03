import subprocess
from ipaddress import IPv4Address


def host_range_ping(start_ip, end_ip):
    # Преобразуем начальный и конечный адреса в объекты IPv4Address
    start = IPv4Address(start_ip)
    end = IPv4Address(end_ip)

    # Перебираем все адреса в диапазоне
    for ip in range(int(start), int(end) + 1):
        current_ip = IPv4Address(ip)
        # Заменяем последний октет адреса на текущее значение
        current_ip_str = str(current_ip).rsplit('.', 1)[0] + '.' + str(current_ip).rsplit('.', 1)[1]

        # Вызываем ping для текущего адреса
        result = subprocess.run(['ping', '-c', '1', '-W', '1', current_ip_str], stdout=subprocess.DEVNULL)

        if result.returncode == 0:
            print(f"Host {current_ip_str} is reachable")
        else:
            print(f"Host {current_ip_str} is not reachable")


if __name__ == "__main__":
    start_ip = '192.168.0.1'
    end_ip = '192.168.0.10'
    host_range_ping(start_ip, end_ip)
