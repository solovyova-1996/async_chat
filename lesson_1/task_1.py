# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и
# проверить тип и содержание соответствующих переменных.
# атем с помощью онлайн-конвертера преобразовать строковые
# представление в формат Unicode и также проверить тип и содержимое
# переменных.
words_list = list(map(type, ['разработка', 'сокет', 'декоратор']))
print(*words_list)
words_list_unicode = list(map(type, [b'%u0440%u0430%u0437%u0440%u0430%u0431%u043E%u0442%u043A%u0430',
                                     b'%u0441%u043E%u043A%u0435%u0442',
                                     b'%u0434%u0435%u043A%u043E%u0440%u0430%u0442%u043E%u0440']))
print(*words_list_unicode)


# <class 'str'> <class 'str'> <class 'str'>
# <class 'bytes'> <class 'bytes'> <class 'bytes'>
