# Setver connection & transport protocol utils
from gb_python_async01.client.config import ClientConfig
from gb_python_async01.transport.errors import *
from gb_python_async01.transport.model.message import *
from gb_python_async01.transport.endpoints import ClientEndpoint
from gb_python_async01.transport.protocol import JIMSerializer


class ClientTransport():
    def __init__(self, logger, config: ClientConfig):
        self.config = config
        self.logger = logger
        self.user = config.user_name

        self.serializer = JIMSerializer()
        self.lock = None
        self.waiting_time = 0.1

        self.srv_host = config.srv_host
        self.srv_port = config.srv_port

    def connect(self):

        self.conn = ClientEndpoint(logger=self.logger, message_max_size=self.config.message_max_size)

        try:
            # Connecting to server
            self.logger.info(f'Connecting to {self.srv_host}:{self.srv_port}, user {self.user}')
            # Reading and writing in one socket -> timeout needed for resource lock releasing
            self.conn.connect_to_server(host=self.srv_host, port=self.srv_port, timeout=1)

            return True

        except (EndpointCommunicationError, Exception) as e:
            self.logger.critical(e)
            self.conn.close()

        return False

    def send_action(self, msg: Action) -> Response:
        self.logger.debug(f'{self.user} Sending {msg}')
        self.conn.put_message(self.serializer.encode_action(msg))
        response = self.serializer.decode_response(self.conn.get_message())
        self.logger.debug(f'{self.user} Response {response}')
        if response.is_error:
            self.logger.error(f'{self.user} Error response on {msg.action} message: {response}')
        return response

    def read_action(self) -> Action:
        action = self.serializer.decode_action(self.conn.get_message())
        self.logger.debug(f'{self.user} Accepting {action}')
        self.conn.put_message(self.serializer.encode_response(Response200()))
        return action
