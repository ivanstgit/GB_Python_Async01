# Интерфейс командной строки для ввода команд

from datetime import datetime, timedelta
import threading
from gb_python_async01.client.config import ClientConfig

from gb_python_async01.client.controller import ClientController
from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.utils.observer import Observer


class ClientCLI(Observer):
    def __init__(self, config: ClientConfig, db: ClientStorage, db_lock: threading.Lock, controller: ClientController) -> None:
        self.config = config
        self.db = db
        self.db_lock = db_lock
        self.controller = controller

        self.message_history_pointer = datetime.now() + timedelta(days=-30)
        self.has_new_messages = True

    def sender_loop(self):
        print(f'Welcome, {self.config.user_name}')
        while True:
            # ...

            if self.has_new_messages:
                self.has_new_messages = False
                with self.db_lock:
                    messages = self.db.message_history(contact_name='', limit=5)
                for message in messages:
                    if message.is_inbound:
                        res = f'Получено {message.created_at}, {message.contact_id}:\n {message.msg_txt}'
                    else:
                        res = f'Отправлено {message.created_at}, {message.contact_id}:\n {message.msg_txt}'
                    print(res)
                    self.message_history_pointer = max(self.message_history_pointer, message.created_at)

            EXIT_COMMAND = 'exit'
            MESSAGE_COMMAND = 'message'
            ADD_CONTACT_COMMAND = 'addcontact'
            DEL_CONTACT_COMMAND = 'delcontact'
            txt = f"Введите команду ({'/'.join([EXIT_COMMAND, MESSAGE_COMMAND, ADD_CONTACT_COMMAND, DEL_CONTACT_COMMAND])}): "
            command = input(txt)
            if command == '':
                continue
            elif command == EXIT_COMMAND:
                self.controller.send_exit()
            elif command == ADD_CONTACT_COMMAND:
                contact = input(f'Введите контакт: ')
                self.controller.add_contact(contact)
            elif command == DEL_CONTACT_COMMAND:
                contact = input(f'Введите контакт: ')
                self.controller.del_contact(contact)
            else:
                msg_txt = input(f'Введите сообщение в чат: ')
                receiver = input(f'Введите адресата: ')
                self.controller.send_message(receiver, msg_txt)

    def modelChanged(self):
        self.has_new_messages = True
