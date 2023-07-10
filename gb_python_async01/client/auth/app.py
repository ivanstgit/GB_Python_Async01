import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication

from gb_python_async01.client.auth.gui import LoginWindow
from gb_python_async01.client.transport import ClientTransport


class ClientLoginGUI:
    """QT приложение для ввода логина/пароля"""

    def run(
        self,
        logger,
        transport: ClientTransport,
        user_name: Optional[str],
        password: Optional[str],
    ):
        """ """
        client_app = QApplication(sys.argv)
        view = LoginWindow(logger, transport, user_name, password)
        view.show()

        client_app.exec_()
