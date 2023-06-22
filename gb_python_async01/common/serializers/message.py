from gb_python_async01.common.model.message import *


class MessageSerializer():
    action = 'action'

    time = 'time'

    user = 'user'
    user_account = 'account_name'
    user_status = 'status'

    receiver = 'to'
    sender = 'from'
    message = 'message'

    response = 'response'
    error = 'error'
    alert = 'alert'

    @staticmethod
    def to_dict(msg: Message):
        pass

    @staticmethod
    def from_dict(msg: dict):
        pass


class ActionPresenceSerializer(MessageSerializer):
    def to_dict(self, msg: ActionPresence) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user: {
                self.user_account: msg.user_account,
                self.user_status: msg.user_status
            }
        }

    def from_dict(self, msg: dict) -> ActionPresence:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        user = msg.get(self.user)
        if not user:
            raise JIMValidationError(self.user)
        try:
            return ActionPresence(time=time,
                                  user_account=user.get(self.user_account),
                                  user_status=user.get(self.user_status))
        except Exception as e:
            raise JIMValidationError


class ActionMessageSerializer(MessageSerializer):

    def to_dict(self, msg: ActionMessage) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.receiver: msg.receiver,
            self.sender: msg.sender,
            self.message: msg.message
        }

    def from_dict(self, msg: dict) -> ActionMessage:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        message = msg.get(self.message)
        if not message:
            raise JIMValidationError(self.time)
        try:
            return ActionMessage(time=time,
                                 receiver=msg.get(self.receiver),
                                 sender=msg.get(self.sender),
                                 message=message)
        except Exception as e:
            raise JIMValidationError


class ActionExitSerializer(MessageSerializer):

    def to_dict(self, msg: ActionExit) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time
        }

    def from_dict(self, msg: dict) -> ActionExit:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        message = msg.get(self.message)
        if not message:
            raise JIMValidationError(self.time)
        try:
            return ActionExit(time=time)
        except Exception as e:
            raise JIMValidationError


class ResponseSerializer(MessageSerializer):
    def to_dict(self, msg: Response) -> dict:
        res = {self.response: str(msg.response)}
        if msg.error:
            res[self.error] = msg.error
        if msg.alert:
            res[self.alert] = msg.alert

        return res

    def from_dict(self, msg: dict) -> Response:
        response = msg.get(self.response)
        if not response:
            raise JIMValidationError(field=self.response)
        message = msg.get(self.alert) or msg.get(self.error) or ''
        try:
            return Response(int(response), message)
        except Exception as e:
            raise JIMValidationError
