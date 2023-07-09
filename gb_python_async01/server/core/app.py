# Основная задача корневого приложения - обслуживание подключенных клиентов (т.е. по сути это View)
# В приложении 2 модели:
#  - пользовательская сессия: создается под каждый сокет, хранит его состояние и очереди сообщений,
#    обрабатывает сообщения в контексте пользователя (авторизация, шифрование)
#  - менеджер сессий: хранение перечня клиентских сессий, "стыковка" их с сокетами и друг с другом
#    (исходящие сообщения сначала обрабатываются в сессии отправителя, затем - получателя)
# Состояние моделей меняется соответствующими сетевыми сообщениями.

import select
import threading

from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.core.session_manager import ClientSessionManager
from gb_python_async01.server.db.user_view import ServerStorage
from gb_python_async01.transport.endpoints import *


class ServerCore():

    def __init__(self, logger, config: ServerConfig, db: ServerStorage):
        self.config = config
        self.logger = logger
        self.db = db
        self.conn = ServerEndpoint(logger=self.logger, message_max_size=self.config.message_max_size)

    def run(self, raise_on_error: threading.Event, terminate_on: threading.Event, mainloop_timeout=1):
        try:

            self.conn.start_server(self.config.host, self.config.port,  # type: ignore
                                   self.config.connection_limit,
                                   self.config.timeout)

            sm = ClientSessionManager(self.logger, self.db)

            while not terminate_on.isSet():
                outputs = sm.get_client_endpoints()
                inputs = outputs.copy()
                inputs.append(self.conn)

                reads, send, excepts = select.select(inputs, outputs, inputs, mainloop_timeout)

                # список READS - сокеты, готовые к чтению
                for client in reads:
                    if client == self.conn:
                        # на серверный сокет приходит запрос на подключение клиента
                        sm.add_client(self.conn.get_client())
                    else:
                        # определяем сессию (обработчик)
                        cl = sm.get_client_session(client)
                        if cl:
                            try:
                                # читаем сообщение из сокета
                                msg = client.get_message()
                            except Exception as e:
                                # Клиент отключился
                                sm.remove_client(client)
                            else:
                                # Передаем в сессию (обработчик)
                                cl.process_inbound_message(msg)

                # список SEND - сокеты, готовые принять сообщение
                for client in send:
                    cl = sm.get_client_session(client)
                    if cl:
                        msg = cl.get_next_out_message()
                        if msg:
                            try:
                                client.put_message(msg)
                            except Exception as e:
                                # Клиент отключился
                                sm.remove_client(client)

                # список EXCEPTS - сокеты, в которых произошла ошибка
                for client in excepts:
                    sm.remove_client(client)

        except Exception as e:
            self.logger.critical(f'Server error {e}')
            raise_on_error.set()
        finally:
            self.conn.close()
