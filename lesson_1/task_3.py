# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
for word in "attribute","класс","функция","type":
    print(word.encode('utf-8'))
    print(type(word.encode('utf-8')))
# b'attribute'
# <class 'bytes'>
# b'\xd0\xba\xd0\xbb\xd0\xb0\xd1\x81\xd1\x81'
# <class 'bytes'>
# b'\xd1\x84\xd1\x83\xd0\xbd\xd0\xba\xd1\x86\xd0\xb8\xd1\x8f'
# <class 'bytes'>
# b'type'
# <class 'bytes'>
# Слова attribute и type невозможно записать в байтовом типе
