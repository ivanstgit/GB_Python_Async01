# ### 3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата. Для этого:
# Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список,
# второму — целое число, третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом,
# отсутствующим в кодировке ASCII (например, €);
# Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
# При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
# Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.

import yaml
from yaml.loader import SafeLoader
import os

FILENAME = os.path.join('gb_python_async01', 'lesson_02', 'task_03_result.yaml')

CONTENT = {'param_list': ['item 01', 'элемент 2'],
           'param_int4': 4,
           'param_dict': {'key1': '€ + ¥',
                          'key2': '§ ® Ыыы'
                          }
           }

with open(FILENAME, 'w', encoding='utf-8') as f:
    yaml.dump(CONTENT, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open(FILENAME, 'r', encoding='utf-8') as f:
    test = yaml.load(f, Loader=SafeLoader)

if CONTENT == test:
    print('OK')
else:
    print('Error')
