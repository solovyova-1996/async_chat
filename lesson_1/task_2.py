# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
# (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.
words_list = ['class', 'function', 'method']
for word in words_list:
    bytes_word = bytes(word, encoding='utf-8')
    print(f'{word}\ntype:{type(bytes_word)} value:{bytes_word} {len(bytes_word)}')

# class
# type:<class 'bytes'> value:b'class' 5
# function
# type:<class 'bytes'> value:b'function' 8
# method
# type:<class 'bytes'> value:b'method' 6