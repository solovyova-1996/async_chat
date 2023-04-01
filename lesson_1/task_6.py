# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно
# открыть файл в формате Unicode и вывести его содержимое.
from chardet.universaldetector import UniversalDetector

detector = UniversalDetector()

with open('test_file.txt', 'rb') as file:
    result = file.readlines()
for line in result:
    detector.feed(line)
    if detector.done:
        break
detector.close()

encoding_res = detector.result.get('encoding')

print(f'Кодировка файла по умолчанию {encoding_res}')

with open('test_file.txt', 'r', encoding=encoding_res) as file:
    print(file.read())
