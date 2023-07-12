from gbmessclient12345.common.transport.model.message import *


class JIMMessageSerializer:
    auth_action = "auth_action"
    data1 = "secret1"
    data2 = "secret2"

    action = "action"

    time = "time"

    user = "user"
    user_account = "account_name"
    user_status = "status"

    receiver = "to"
    sender = "from"
    message = "message"

    contact = "contact"

    response = "response"
    error = "error"
    alert = "alert"
    data = "data"

    @staticmethod
    def to_dict(msg: JIMMessage):
        pass

    @staticmethod
    def from_dict(msg: dict):
        pass


class JIMAuthSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMAuth) -> dict:
        return {
            self.auth_action: msg.auth_action,
            self.data1: msg.data1,
            self.data2: msg.data2,
        }

    def from_dict(self, msg: dict) -> JIMAuth:
        auth_action = msg.get(self.auth_action) or ""
        if not auth_action:
            raise JIMValidationError(self.user)

        data1 = msg.get(self.data1) or ""
        data2 = msg.get(self.data2) or ""
        return JIMAuth(auth_action, data1, data2)


class JIMActionPresenceSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMActionPresence) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user: {
                self.user_account: msg.user_account,
                self.user_status: msg.user_status,
            },
        }

    def from_dict(self, msg: dict) -> JIMActionPresence:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        user = msg.get(self.user)
        if not user:
            raise JIMValidationError(self.user)
        try:
            return JIMActionPresence(
                time=time,
                user_account=user.get(self.user_account),
                user_status=user.get(self.user_status),
            )
        except Exception as e:
            raise JIMValidationError


class JIMActionMessageSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMActionMessage) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.receiver: msg.receiver,
            self.sender: msg.sender,
            self.message: msg.message,
        }

    def from_dict(self, msg: dict) -> JIMActionMessage:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        message = msg.get(self.message)
        if not message:
            raise JIMValidationError(self.time)
        try:
            return JIMActionMessage(
                time=time,
                receiver=msg.get(self.receiver),
                sender=msg.get(self.sender),
                message=message,
            )
        except Exception as e:
            raise JIMValidationError


class JIMActionExitSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMActionExit) -> dict:
        return {self.action: msg.action, self.time: msg.time}

    def from_dict(self, msg: dict) -> JIMActionExit:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        try:
            return JIMActionExit(time=time)
        except Exception as e:
            raise JIMValidationError


class JIMActionGetContactsSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMActionGetContacts) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user_account: msg.user_account,
        }

    def from_dict(self, msg: dict) -> JIMActionGetContacts:
        time = msg.get(self.time)
        if not time:
            raise JIMValidationError(self.time)

        user_account = msg.get(self.user_account)
        if not user_account:
            raise JIMValidationError(self.user_account)
        try:
            return JIMActionGetContacts(time=time, user_account=user_account)
        except Exception as e:
            raise JIMValidationError


class JIMActionAddDelContactSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMActionAddContact or JIMActionDeleteContact) -> dict:
        return {
            self.action: msg.action,
            self.time: msg.time,
            self.user_account: msg.user_account,
            self.contact: msg.contact,
        }

    def from_dict(self, msg: dict) -> JIMAction:
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
            if action == JIMActionAddContact.get_action():
                return JIMActionAddContact(
                    time=time, user_account=user_account, contact=contact
                )
            elif action == JIMActionDeleteContact.get_action():
                return JIMActionDeleteContact(
                    time=time, user_account=user_account, contact=contact
                )
        except Exception as e:
            raise JIMValidationError
        raise JIMValidationError(self.action)


class JIMResponseSerializer(JIMMessageSerializer):
    def to_dict(self, msg: JIMResponse) -> dict:
        res = {self.response: str(msg.response)}
        if msg.error:
            res[self.error] = msg.error
        if msg.alert:
            res[self.alert] = msg.alert
        if msg.data:
            res[self.data] = msg.data
        return res

    def from_dict(self, msg: dict) -> JIMResponse:
        response = msg.get(self.response)
        if not response:
            raise JIMValidationError(field=self.response)
        message = msg.get(self.alert) or msg.get(self.error) or ""
        data = msg.get(self.data) or None
        try:
            return JIMResponse(int(response), message, data)
        except Exception as e:
            raise JIMValidationError(e)
