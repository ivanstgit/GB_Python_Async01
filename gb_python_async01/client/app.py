
from queue import Queue
import threading
import time
from gb_python_async01.client.cli import ClientCLI
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

    def run(self):
        self.db = ClientStorage(db_url=self.config.db_url)
        self.db.init_db_tables()
        self.db_lock = threading.Lock()

        self.transport = ClientTransport(self.logger, self.config)
        self.server_lock = threading.Lock()

        self.controller = ClientController(
            config=self.config, logger=self.logger,
            db=self.db, db_lock=self.db_lock,
            transport=self.transport,
            server_lock=self.server_lock)

        # self.cli = ClientCLI(
        #     config=self.config,
        #     db=self.db, db_lock=self.db_lock,
        #     controller=self.controller)

        # self.controller.addObserver(self.cli)

        self.gui = ClientGUI(self.config, self.db, self.controller)

        try:
            self.logger.debug(f'{self.config.user_name} Connecting to server')
            if not self.transport.connect():
                return

            error_txt = self.controller.send_presence()
            if error_txt:
                self.logger.error(f'{self.config.user_name} Error on presence: {error_txt}')
                return

            # Тут какой-то полный треш в ТЗ - вообще не ясно, зачем хранить контакты и на клиенте, и на сервере..
            # Вероятно, просто кеширование; или для ссылочной целостности с сообщениями
            self.logger.debug(f'{self.config.user_name} Synchronizing contacts')
            error_txt = self.controller.synchonize_contacts_from_server()
            if error_txt:
                self.logger.error(f'{self.config.user_name} Error while contact synchronization: {error_txt}')

            self.logger.debug(f'{self.config.user_name} Starting server integration thread')
            thread_reader = threading.Thread(target=self.controller.reader_loop, name='Reader', args=())
            thread_reader.daemon = True
            thread_reader.start()
            self.logger.debug(f'{self.config.user_name} Reader thread started')

            self.gui.run(thread_reader)
            # time.sleep(0.5)
            # thread_sender = threading.Thread(target=self.gui.run, name='Sender', args=())
            # thread_sender.daemon = True
            # thread_sender.start()
            # self.logger.debug(f'{self.config.user_name} Sender thread started')

            # # Main loop
            # while True:
            #     time.sleep(1)

            #     if thread_sender.is_alive():  # and thread_reader.is_alive():
            #         continue
            #     self.logger.debug(f'{self.config.user_name} Client stopped...')
            #     break

        except Exception as e:
            self.logger.critical(e)
        finally:
            pass