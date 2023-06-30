import threading
import time
from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.db.view import ServerStorage
from gb_python_async01.server.gui.app import ServerGUI
from gb_python_async01.server.log.config import ServerLogger
from gb_python_async01.server.message_dispatcher import ServerMessageDispatcher


class ServerApp():
    """ Server Application:
    Message dispatcher: client interaction thread (controller -> DB model, client sockets)
    GUI: Qt thread (reading view on DB & changing view on config model)
    Main thread: starts GUI and dispatcher in separate threads, config controller (restarts threads if config changed)
    """

    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = ServerLogger(self.config.logger_file_path, self.config.debug, self.config.testing).logger

    def run(self):

        config_changed = threading.Event()

        self._start_db()
        thread_message_dispatcher = self._start_message_dispatcher(terminate_on=config_changed)
        thread_gui = self._start_gui(to_terminate=config_changed)

        while True:
            time.sleep(1)
            if config_changed is None or config_changed.isSet():
                self.logger.debug(f'(Re)starting threads: {self.config}')
                config_changed = threading.Event()
                self._start_db()
                thread_message_dispatcher = self._start_message_dispatcher(terminate_on=config_changed)
                thread_gui = self._start_gui(to_terminate=config_changed)

            if thread_message_dispatcher.is_alive() and thread_gui.is_alive():
                continue
            self.logger.debug(f'Server stopped...')
            break

    def _start_db(self):
        self.db = ServerStorage(self.config.db_url)
        self.db.init_db_tables()
        self.db.clear_active_connections()

    def _start_message_dispatcher(self, terminate_on: threading.Event) -> threading.Thread:
        self.message_dispatcher = ServerMessageDispatcher(self.logger, self.config, self.db)
        thread = threading.Thread(target=self.message_dispatcher.run, name='Message dispatcher', args=(terminate_on,))
        thread.daemon = True
        thread.start()
        self.logger.debug(f'Message dispatcher thread started')
        return thread

    def _start_gui(self, to_terminate: threading.Event) -> threading.Thread:
        self.gui = ServerGUI(config=self.config, db=self.db)
        thread = threading.Thread(target=self.gui.run, name='GUI dispatcher', args=(to_terminate,))
        thread.daemon = True
        thread.start()
        self.logger.debug(f'GUI thread started')
        return thread
