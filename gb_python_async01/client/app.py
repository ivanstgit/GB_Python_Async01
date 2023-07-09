import threading
from typing import Optional
from gb_python_async01.client.auth.app import ClientLoginGUI

from gb_python_async01.client.config import ClientConfig
from gb_python_async01.client.controller import ClientController
from gb_python_async01.client.db.view import ClientStorage
from gb_python_async01.client.gui.app import ClientGUI
from gb_python_async01.client.log.config import ClientLogger
from gb_python_async01.client.transport import ClientTransport


class ClientApp():
    """ 
    Main client app
    Manage components and threads

    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = ClientLogger(self.config.logger_file_path, self.config.debug, self.config.testing).logger

    def run(self, user_name: Optional[str], password: Optional[str]):
        # Инициализируем транспорт
        self.transport = ClientTransport(self.config)

        # Диалог авторизации
        self.logger.debug(f'Connecting to server')
        login_app = ClientLoginGUI()
        login_app.run(self.logger, self.transport, user_name, password)
        if not self.transport.user:
            return

        # После авторизации адаптируем настройки, зависящие от пользователя
        self.config.after_login(self.transport.user)
        self.logger = ClientLogger(self.config.logger_file_path, self.config.debug, self.config.testing).logger

        # Инициализируем базу
        self.db = ClientStorage(db_url=self.config.db_url)
        self.db.init_db_tables()
        self.db_lock = threading.Lock()

        # Инициализируем компоненты основного приложения
        self.server_lock = threading.Lock()
        self.controller = ClientController(
            config=self.config, logger=self.logger,
            db=self.db, db_lock=self.db_lock,
            transport=self.transport,
            server_lock=self.server_lock)

        self.gui = ClientGUI(self.config, self.db, self.controller)

        try:
            # Обновление данных с сервера
            # Сначала неполученные сообщения
            self.controller.reader_loop(terminate_on_first_timeout=True)

            self.logger.debug(f'{self.config.user_name} Synchronizing contacts')
            error_txt = self.controller.synchonize_contacts_from_server()
            if error_txt:
                self.logger.error(f'{self.config.user_name} Error while contact synchronization: {error_txt}')

            error_txt = self.controller.send_presence()
            if error_txt:
                self.logger.error(f'{self.config.user_name} Error on presence: {error_txt}')
                return

            # Запускаем потоки: для GUI и для приема входящих сообщений
            self.logger.debug(f'{self.config.user_name} Starting server integration thread')
            thread_reader = threading.Thread(target=self.controller.reader_loop, name='Reader', args=())
            thread_reader.daemon = True
            thread_reader.start()
            self.logger.debug(f'{self.config.user_name} Reader thread started')

            self.gui.run(thread_reader)

        except Exception as e:
            self.logger.critical(e)
        finally:
            self.controller.send_exit()
