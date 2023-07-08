from copy import copy
import threading
import time
from gb_python_async01.server.config import ServerConfig
from gb_python_async01.server.db.user_session_view import UserSessionView
from gb_python_async01.server.db.user_view import ServerStorage
from gb_python_async01.server.gui.app import ServerGUI
from gb_python_async01.server.log.config import ServerLogger
from gb_python_async01.server.core.app import ServerCore


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
        self.logger.info(f'Starting threads: {self.config}')
        self._start_threads()

        while True:
            time.sleep(1)
            # config was changed - restart threads
            if self.ev_config_changed.isSet():
                config_before = copy(self.config)

                try:
                    self._stop_threads()
                    self.config = self.config_editable
                    self.logger.info(f'Restarting threads: {self.config}')
                    self._start_threads()
                except Exception as e:
                    self._stop_threads()
                    self.logger.info(f'Error restarting threads {e}, use previous config')
                    self.config = config_before
                    self._start_threads()

            if self.thread_message_dispatcher and self.thread_message_dispatcher.is_alive():
                # Server can work without GUI, even start w/o GUI
                continue
            self.logger.info(f'Server stopped...')
            break

    def _start_threads(self):
        self.ev_config_changed = threading.Event()
        self.ev_core_error = threading.Event()
        self.config_editable = copy(self.config)

        self.db = ServerStorage(self.config.db_url)
        self.db.adm_init_db_tables()

        self.thread_message_dispatcher = self._start_message_dispatcher(terminate_on=self.ev_config_changed, termination=self.ev_core_error)
        if self.config.gui_enabled:
            self.thread_gui = self._start_gui(config_editable=self.config_editable, config_changed_event=self.ev_config_changed, terminate_on=self.ev_core_error)

    def _stop_threads(self):
        if self.thread_message_dispatcher:
            for i in range(30):
                if self.thread_message_dispatcher.is_alive():
                    time.sleep(1)
            if self.thread_message_dispatcher.is_alive():
                self.logger.critical('Error stopping dispatcher thread')
        if self.thread_gui:
            for i in range(30):
                if self.thread_gui.is_alive():
                    time.sleep(1)
            if self.thread_gui.is_alive():
                self.logger.critical('Error stopping gui thread')
        if self.db:
            self.db.stop()

    def _start_message_dispatcher(self, terminate_on: threading.Event, termination: threading.Event) -> threading.Thread:
        self.message_dispatcher = ServerCore(self.logger, self.config, self.db)
        thread = threading.Thread(target=self.message_dispatcher.run, name='Message dispatcher', args=(termination, terminate_on,))
        thread.daemon = True
        thread.start()
        self.logger.debug(f'Message dispatcher thread started')
        return thread

    def _start_gui(self, config_editable, config_changed_event: threading.Event, terminate_on: threading.Event) -> threading.Thread:
        self.gui = ServerGUI(config=self.config, config4edit=config_editable, db=self.db)
        thread = threading.Thread(target=self.gui.run, name='GUI dispatcher', args=(config_changed_event, terminate_on, ))
        thread.daemon = True
        thread.start()
        self.logger.debug(f'GUI thread started')
        return thread
