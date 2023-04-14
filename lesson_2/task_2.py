# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON
# с информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными.
# Для этого:
# Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item),
# количество (quantity), цена (price), покупатель (buyer), дата (date).
# Функция должна предусматривать запись данных в виде словаря в файл orders.json.
# При записи данных указать величину отступа в 4 пробельных символа;
# Проверить работу программы через вызов функции write_order_to_json() с
# передачей в нее значений каждого параметра.
import json
from datetime import datetime

item = 'кушетка'
quantity = 7
price = 1500
buyer = "Виктор"
date = str(datetime.now())


def write_order_to_json(item, quantity, price, buyer, date):
    """
    Function that writes data to json
    :param item: Product Name
    :param quantity: quantity product
    :param price: price product
    :param buyer:buyer
    :param date: date of purchase
    """
    data = {"item": item, "quantity": quantity, "price": price, "buyer": buyer, "date": date}
    with open('orders.json', 'w') as file:
        file.write(json.dumps(data, sort_keys=True, indent=4))
    with open('orders.json', 'r') as file:
        read_file = file.read()
        res = json.loads(read_file)
        print(res)


if __name__ == '__main__':
    write_order_to_json(item, quantity, price, buyer, date)
