import subprocess
from ipaddress import IPv4Address
from tabulate import tabulate


def host_range_ping_tab(start_ip, end_ip):
    # Преобразуем начальный и конечный адреса в объекты IPv4Address
    start = IPv4Address(start_ip)
    end = IPv4Address(end_ip)

    # Собираем результаты проверки адресов в список
    results = []
    for ip in range(int(start), int(end) + 1):
        current_ip = IPv4Address(ip)
        # Заменяем последний октет адреса на текущее значение
        current_ip_str = str(current_ip).rsplit('.', 1)[0] + '.' + str(current_ip).rsplit('.', 1)[1]

        # Вызываем ping для текущего адреса
        result = subprocess.run(['ping', '-c', '1', '-W', '1', current_ip_str], stdout=subprocess.DEVNULL)

        if result.returncode == 0:
            status = "reachable"
        else:
            status = "not reachable"

        # Добавляем результат проверки в список
        results.append((current_ip_str, status))

    # Выводим результаты в таблице
    print(tabulate(results, headers=["IP address", "Status"], tablefmt="pretty"))


if __name__ == '__main__':
    start_ip = '192.168.0.1'
    end_ip = '192.168.0.10'
    host_range_ping_tab(start_ip, end_ip)
