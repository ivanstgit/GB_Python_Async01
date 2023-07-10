"""Классы-абстракции для обеспечения передачи данных"""
import socket

from gb_python_async01.transport.errors import (
    EndpointCommunicationError,
    EndpointTimeout,
)
from gb_python_async01.transport.metaclasses import (
    EndpointVerifier,
    ClientEndpointVerifier,
    ServerEndpointVerifier,
)


class Endpoint(metaclass=EndpointVerifier):
    """Базовый класс подключения"""

    def __init__(self, message_max_size, address=(), from_existing_resource=None):
        if from_existing_resource:
            self.resource = from_existing_resource
        else:
            self.resource = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encoding = "utf-8"
        self.maxsize = message_max_size
        self.address = address

    def __enter__(self):
        return self.resource

    def __exit__(self, *args):
        self.close()

    def __str__(self):
        return f"{str(self.resource)} at {str(self.address)}"

    def __hash__(self) -> int:
        return self.fileno()

    def __eq__(self, __value: object) -> bool:
        if hasattr(__value, "fileno"):
            return self.fileno() == __value.fileno()  # type: ignore
        return False

    def put_message(self, message: bytes):
        try:
            self.resource.send(message)
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as e:
            raise EndpointCommunicationError(e)

    def get_message(self) -> bytes:
        try:
            data = self.resource.recv(self.maxsize)
            return data
        except socket.timeout:
            raise EndpointTimeout()
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as e:
            raise EndpointCommunicationError(e)

    def fileno(self):
        return self.resource.fileno()

    def close(self):
        self.resource.close()


class ClientEndpoint(Endpoint, metaclass=ClientEndpointVerifier):
    """Подключение со стороны клиентского приложения"""

    def connect_to_server(self, host: str, port: int, timeout=0.0):
        try:
            if timeout > 0.0:
                self.resource.settimeout(timeout)
            self.resource.connect((host, port))
            self.is_connected = True
        except ConnectionRefusedError as e:
            self.is_connected = False
            raise EndpointCommunicationError(e)


class ServerEndpoint(Endpoint, metaclass=ServerEndpointVerifier):
    """Подключение со стороны серверного приложения (основной сокет, принимающий клиентов)"""

    def __init__(self, logger, message_max_size):
        super().__init__(
            message_max_size,
        )
        self.logger = logger

    def start_server(self, host: str, port: int, connection_limit: int, timeout: float):
        try:
            self.logger.info(f"Starting server on {host}:{port}", stacklevel=2)
            self.resource.bind((host, port))
            if timeout:
                self.resource.settimeout(timeout)
            if connection_limit:
                self.resource.listen(connection_limit)
            self.is_connected = True
        except ConnectionRefusedError as e:
            self.is_connected = False
            self.logger.critical(f"Connection error {e}")
            raise EndpointCommunicationError(e)

    def get_client(self):
        try:
            client, client_address = self.resource.accept()
            self.logger.debug(f"Client {client_address} connected")
        except OSError as e:
            raise EndpointCommunicationError(e)
        else:
            return Endpoint(
                self.maxsize, address=client_address, from_existing_resource=client
            )
