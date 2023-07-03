from gb_python_async01.transport.model.message import *


class MessageSerializer():
    action = 'action'

    time = 'time'

    user = 'user'
    user_account = 'account_name'
    user_status = 'status'

    receiver = 'to'
    sender = 'from'
    message = 'message'

    contact = 'contact'

    response = 'response'
    error = 'error'
    alert = 'alert'
    data = 'data'

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

        try:
            return ActionExit(time=time)
        except Exception as e:
            raise JIMValidationError


class ActionGetContactsSerializer(MessageSerializer):
    def to_dict(self, msg: ActionGetContacts) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user_account: msg.user_account
        }

    def from_dict(self, msg: dict) -> ActionGetContacts:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        user_account = msg.get(self.user_account)
        if not user_account:
            raise JIMValidationError(self.user_account)
        try:
            return ActionGetContacts(time=time, user_account=user_account)
        except Exception as e:
            raise JIMValidationError


class ActionAddDelContactSerializer(MessageSerializer):
    def to_dict(self, msg: ActionAddContact or ActionDeleteContact) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user_account: msg.user_account,
            self.contact: msg.contact
        }

    def from_dict(self, msg: dict) -> Action:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        user_account = msg.get(self.user_account)
        if not user_account:
            raise JIMValidationError(self.user_account)

        contact = msg.get(self.contact)
        if not contact:
            raise JIMValidationError(self.contact)

        try:
            action = msg.get(self.action)
            if action == ActionAddContact.get_action():
                return ActionAddContact(time=time, user_account=user_account, contact=contact)
            elif action == ActionDeleteContact.get_action():
                return ActionDeleteContact(time=time, user_account=user_account, contact=contact)
        except Exception as e:
            raise JIMValidationError
        raise JIMValidationError(self.action)


class ResponseSerializer(MessageSerializer):
    def to_dict(self, msg: Response) -> dict:
        res = {self.response: str(msg.response)}
        if msg.error:
            res[self.error] = msg.error
        if msg.alert:
            res[self.alert] = msg.alert
        if msg.data:
            res[self.data] = msg.data
        return res

    def from_dict(self, msg: dict) -> Response:
        response = msg.get(self.response)
        if not response:
            raise JIMValidationError(field=self.response)
        message = msg.get(self.alert) or msg.get(self.error) or ''
        data = msg.get(self.data) or None
        try:
            return Response(int(response), message, data)
        except Exception as e:
            raise JIMValidationError(e)