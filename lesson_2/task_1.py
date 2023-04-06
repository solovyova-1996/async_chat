# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
# определенных данных из
# файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными,
# их открытие и считывание данных.
# В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
# соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
# os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
# поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
# «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл
# main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
# В этой функции реализовать получение данных
# через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv()
import csv
import re

os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
file_list_csv = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def find_string(lst, str_find, str_sample):
    """
    Function that finds the desired substring and adds data to the string
    :param lst: list to add rows
    :param str_find: string in which to search for a substring
    :param str_sample:search string pattern
    """
    match = re.findall(str_sample, str(str_find))
    if len(match):
        lst.append(str_find[0].split(":")[-1].rstrip().lstrip())


def get_data(file_list, os_prod_list, os_name_list, os_code_list, os_type_list):
    """
    Function that prepares data for writing to file csv
    :param file_list: filename list
    :param os_prod_list: os prod list
    :param os_name_list: os name list
    :param os_code_list: os code list
    :param os_type_list: os typelist
    :return: list with tuples
    """
    main_data = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    for file_csv in file_list:
        with open(file_csv, 'r') as file:
            data_from_file = csv.reader(file)
            for row in data_from_file:
                find_string(os_prod_list, row, r"\['Изготовитель системы:")
                find_string(os_name_list, row, r"\['Название ОС:")
                find_string(os_code_list, row, r"\['Код продукта:")
                find_string(os_type_list, row, r"\['Тип системы:")
    return [tuple(main_data)] + list(zip(*[os_prod_list, os_name_list, os_code_list, os_type_list]))


def write_to_csv(file):
    """
    Function of writing data to csv file
    :param file: name file csv
    """
    with open(file, 'w') as file_csv:
        data = get_data(file_list_csv, os_prod_list, os_name_list, os_code_list, os_type_list)
        file_csv_writer = csv.writer(file_csv)
        for row in data:
            file_csv_writer.writerow(row)
    with open(file, 'r') as file:
        print(file.read())


if __name__ == '__main__':
    write_to_csv('res.csv')
