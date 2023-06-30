# Message object
# Под сообщением здесь понимаем любой запрос (action) и ответ (response)
# Не совсем понятно, как правильно организовать/ инкапсулировать логику обработки
# По идее клиент и сервер должны иметь свои контроллеры и работать с объектами
# Но при десериализации все равно будет получаться абстрактный объект (не факт, что разделение action/response будет)..
# Да и хранение скорее всего будет в плоской структуре (и ответы наверно храниться не будут...)
# Поэтому классы ниже - это скорее набор конструкторов к одному объекту с параметрами по умолчанию,
# Вероятно, лучше было бы сделать отдельные методы или общий плоский конструктор/builder + валидаторы...
# from gb_python_async01.transport.model.user import User

from gb_python_async01.transport.errors import JIMValidationError


class Message():
    def __init__(self, type):
        self._type = type

    @property
    def type(self):
        return self._type


class Action(Message):
    @staticmethod
    def get_type():
        return 'action'

    def __init__(self, action, time):
        super().__init__(Action.get_type())
        self._action = action
        self._time = time
        self._user_account = None  # модель пользователя/авторизации/статуса пока не понятна, заглушка
        self._user_status = None
        self._receiver = None
        self._sender = None
        self._message = None
        self._contact = None

    @property
    def action(self):
        return self._action

    @property
    def response(self):
        return None

    @property
    def time(self):
        return self._time

    @property
    def user_account(self):
        return self._user_account

    @property
    def user_status(self):
        return self._user_status

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver

    @property
    def contact(self):
        return self._contact

    @property
    def message(self):
        return self._message

    def __str__(self) -> str:
        return f'Action {self.__dict__}'


class ActionPresence(Action):
    @staticmethod
    def get_action():
        return 'presence'

    def __init__(self, time, user_account: str, user_status: str):
        super().__init__(ActionPresence.get_action(), time)
        self._user_account = user_account
        self._user_status = user_status


class ActionMessage(Action):
    @staticmethod
    def get_action():
        return 'msg'

    def __init__(self, time: float, receiver, sender, message: str):
        super().__init__(ActionMessage.get_action(), time)
        self._receiver = receiver
        self._sender = sender
        self._message = message


class ActionExit(Action):
    @staticmethod
    def get_action():
        return 'quit'

    def __init__(self, time: float):
        super().__init__(ActionExit.get_action(), time)


class ActionGetContacts(Action):
    @staticmethod
    def get_action():
        return 'get_contacts'

    def __init__(self, time: float, user_account: str):
        super().__init__(self.get_action(), time)
        self._user_account = user_account


class ActionAddContact(Action):
    @staticmethod
    def get_action():
        return 'add_contact'

    def __init__(self, time: float, user_account: str, contact: str):
        super().__init__(self.get_action(), time)
        self._user_account = user_account
        self._contact = contact


class ActionDeleteContact(Action):
    @staticmethod
    def get_action():
        return 'del_contact'

    def __init__(self, time: float, user_account: str, contact: str):
        super().__init__(self.get_action(), time)
        self._user_account = user_account
        self._contact = contact


class Response(Message):
    @staticmethod
    def get_type():
        return 'response'

    def __init__(self, response: int, msg='', data=None):
        super().__init__(Response.get_type())
        if response >= 400:
            self._is_error = True
        elif response >= 100:
            self._is_error = False
        else:
            raise JIMValidationError
        self._response = response
        self._message = msg
        self._data = data

    @property
    def is_error(self):
        return self._is_error

    @property
    def response(self):
        return self._response

    @property
    def alert(self):
        if not self.is_error:
            return self._message

    @property
    def error(self):
        if self.is_error:
            return self._message

    @property
    def data(self):
        return self._data

    def __str__(self) -> str:
        return f'Response {self._response}: {self._message}, {self.data}'


class Response200(Response):
    def __init__(self, alert='OK'):
        super().__init__(200, alert)


class Response202(Response):
    def __init__(self, data):
        super().__init__(202, data=data)


class Response400(Response):
    def __init__(self, error='Bad Request'):
        super().__init__(400, error)
