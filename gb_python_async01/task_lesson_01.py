# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание соответствующих переменных.
# Затем с помощью онлайн-конвертера преобразовать строковые представление в формат Unicode и также проверить тип и содержимое переменных.

import locale
import subprocess
import chardet


print(f'Task 01:')
t1_list1 = ['разработка', 'сокет', 'декоратор']
for item in t1_list1:
    print(f'   {item}: {type(item)}')

t1_list2 = ['\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0',
            '\xd1\x81\xd0\xbe\xd0\xba\xd0\xb5\xd1\x82',
            '\xd0\xb4\xd0\xb5\xd0\xba\xd0\xbe\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80']
for item in t1_list2:
    print(f'   {item}: {type(item)}')

# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов (не используя
# методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
print(f'Task 02:')
t2_list = [b'class', b'function', b'method']
for item in t2_list:
    print(f'   {item}: {type(item)}, {len(item)}')

# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
print(f'Task 03:')
t3_list = ['attribute', 'класс', 'функция', 'type']
for item in t3_list:
    try:
        item_test = bytes(item, 'ASCII')
    except UnicodeEncodeError:
        print(f'   {item}: невозможно записать в байтовом типе')

# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в байтовое и выполнить
# обратное преобразование (используя методы encode и decode).
print(f'Task 04:')
t4_list = ['разработка', 'администрирование', 'protocol', 'standard']
for item in t4_list:
    item_enc = item.encode()
    item_dec = item_enc.decode()
    print(f'   {item}=>{item_enc}=>{item_dec} ')

# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый тип на кириллице.
print(f'Task 05:')
t5_list = ['yandex.ru', 'youtube.com']

for item in t5_list:
    subproc_ping = subprocess.Popen(['ping', item], stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:  # type: ignore
        item_dec = line.decode(chardet.detect(line)['encoding'])  # type: ignore
        print(f'   {item_dec} ')
        break

# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор». Проверить
# кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
def_coding = locale.getpreferredencoding()
with open('test_file.txt', encoding='utf-8') as f_n:
    for el_str in f_n:
        print(el_str)
