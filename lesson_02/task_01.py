# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
# info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
# В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в соответствующий список.
# Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list.
# В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить в него названия столбцов отчета
# в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
# В этой функции реализовать получение данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().

import csv
import os
import re

FILEPATH = os.path.join('gb_python_async01', 'lesson_02')


def get_data():
    in_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    os_prod_list = list()
    os_name_list = list()
    os_code_list = list()
    os_type_list = list()
    params = {
        'Изготовитель системы': os_prod_list,
        'Название ОС': os_name_list,
        'Код продукта': os_code_list,
        'Тип системы': os_type_list
    }

    for file in in_files:
        with open(os.path.join(FILEPATH, file), encoding='cp1251') as f:
            content = f.read()

            for param, out_list in params.items():
                regstr = param + r':\s+.*'
                out_list.append(re.compile(regstr).findall(content)[0].split(':')[1].lstrip())
    # print(params)

    main_data = list()
    main_data.append(list(params.keys()))
    for index in range(len(in_files)):
        row = list()
        for param_val in params.values():
            row.append(param_val[index])
        main_data.append(row)
    # print(main_data)
    return main_data


def write_to_csv(file_name):
    data = get_data()
    with open(os.path.join(FILEPATH, file_name), 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n, quoting=csv.QUOTE_NONNUMERIC)
        for row in data:
            f_n_writer.writerow(row)


write_to_csv('task_01_result.csv')
