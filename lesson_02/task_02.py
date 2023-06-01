# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
# Написать скрипт, автоматизирующий его заполнение данными. Для этого:
# Создать функцию write_order_to_json(), в которую передается 5 параметров —
# товар (item), количество (quantity), цена (price), покупатель (buyer), дата (date).
# Функция должна предусматривать запись данных в виде словаря в файл orders.json.
# При записи данных указать величину отступа в 4 пробельных символа;
# Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
import json
import os

FILENAME_INIT = os.path.join('gb_python_async01', 'lesson_02', 'orders init.json')
FILENAME = os.path.join('gb_python_async01', 'lesson_02', 'orders.json')


def write_order_to_json(item, quantity, price, buyer, date):
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except FileNotFoundError:
        with open(FILENAME_INIT, 'r', encoding='utf-8') as f:
            content = json.load(f)

    orders = content['orders']

    with open(FILENAME, 'w', encoding='utf-8', ) as f:
        row = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }
        orders.append(row)
        json.dump(content, f, indent=4, ensure_ascii=False)


write_order_to_json('Поз. 48', 46.2, 500.46, 'Roga inc', '2023-05-28')
