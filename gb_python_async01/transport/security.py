""" Модуль поддержки шифрования сообщений и аутентификации

Аутентификация:

1. клиент отправляет серверу сообщение, содержащее свой открытый ключ;
   сообщение не зашифровано
2. сервер возвращает клиенту сообщение, содержащее сессионный ключ и случайную строку;
   сообщение не зашифровано, но данные в нем зашифрованы открытым ключом клиента
3. клиент отправляет серверу сообщение, содержащее логин и хеш (хеш пароля + строка от сервера);
   сообщение зашифровано сессионным ключом и подписано клиентом
4. сервер проверяет учетные данные и возвращает ответ 200 или 400;
   сообщение сессионным ключом

Обмен сообщениями:

* Сервер шифрует сообщение сессионным ключом и подписывает
* Клиент шифрует сообщение сессионным ключом и подписывает

Текстовые сообщения (контент внутри ActionMessage) шифруются открытым ключом получателя.
"""


import binascii
import hmac
import os

from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP

from gb_python_async01.utils.security import PasswordHash
from gb_python_async01.transport.errors import (
    TransportSecurityAuthError,
    TransportSecurityNoSessionKeyError,
    TransportSecurityValidationError,
)


class TranportEncryption:
    """Базовый класс для обеспечения безопасности клиент/серверного обмена"""

    msg_prefix = b"enc?"
    msg_prefix_len = len(msg_prefix)

    def __init__(self) -> None:
        self._digest_hash_name = "MD5"
        self._session_key_length = 24
        self._salt_length = 128 - self._session_key_length
        self._session_key = None

    @staticmethod
    def check_if_encrypted(msg: bytes) -> bool:
        """Проверить, что сообщение зашифровано"""
        if (
            len(msg) >= TranportEncryption.msg_prefix_len
            and msg[: TranportEncryption.msg_prefix_len]
            == TranportEncryption.msg_prefix
        ):
            return True
        return False

    def encrypt_message(self, message: bytes) -> bytes:
        """Зашифровать сообщение"""
        if self._session_key:
            try:
                cipher_aes = AES.new(self._session_key, AES.MODE_EAX)
                ciphertext, tag = cipher_aes.encrypt_and_digest(
                    self._prepare_to_encrypt(message)
                )
                res = cipher_aes.nonce + tag + ciphertext
                return self.msg_prefix + res
            except Exception:
                raise TransportSecurityValidationError
        raise TransportSecurityNoSessionKeyError

    def decrypt_message(self, message: bytes) -> bytes:
        """Расшифровать сообщение"""
        try:
            message = message[self.msg_prefix_len :]
            nonce = message[:16]
            tag = message[16:32]
            ciphertext = message[32:]
            if self._session_key:
                cipher_aes = AES.new(self._session_key, AES.MODE_EAX, nonce)
                data = cipher_aes.decrypt_and_verify(ciphertext, tag)
                res = self._prepare_after_decrypt(data)
                return res
        except Exception:
            raise TransportSecurityValidationError
        raise TransportSecurityNoSessionKeyError

    def _prepare_to_encrypt(self, text: bytes):
        """Выравнивание сообщения до длины, кратной 16 байтам."""
        pad_len = (16 - len(text) % 16) % 16
        if pad_len == 0:
            spaces_cnt = 15
        else:
            spaces_cnt = pad_len - 1
        res = text + b" " * spaces_cnt + spaces_cnt.to_bytes(1, "little")
        return res

    def _prepare_after_decrypt(self, text: bytes):
        """Обратное преобразование"""
        spaces_cnt = text[-1] + 1
        res = text[:-spaces_cnt]
        return res


class ClientSecurity(TranportEncryption):
    """Класс для обеспечения безопасности со стороны клиента"""

    e2e_prefix = b"e2e?"
    e2e_prefix_len = len(e2e_prefix)

    def __init__(self, key_file_name: str, secret_code: str) -> None:
        super().__init__()
        if os.path.exists(key_file_name):
            with open(key_file_name, mode="rb") as key_file:
                encoded_key = key_file.read()
                key = RSA.import_key(encoded_key, passphrase=secret_code)
        else:
            key = None

        if not key:
            key = RSA.generate(2048)
            encoded_key = key.export_key(
                passphrase=secret_code, pkcs=8, protection="scryptAndAES128-CBC"
            )
            with open(key_file_name, mode="wb") as key_file:
                key_file.write(encoded_key)
        self._key = key
        self._cipher_rsa = PKCS1_OAEP.new(self._key)
        self._server_salt = None

    @property
    def pubkey(self):
        """Открытый ключ клиента"""
        return self._key.public_key().export_key().decode()

    def process_auth_step1(self) -> str:
        """1 шаг аутентификации клиента на сервере"""
        return self.pubkey

    def process_auth_step3(self, message_step2: str, login: str, password: str) -> str:
        """3 шаг аутентификации клиента на сервере"""
        msg_bin = binascii.a2b_base64(message_step2.encode())
        msg_decrypted = self._cipher_rsa.decrypt(msg_bin)
        msg = self._prepare_after_decrypt(msg_decrypted)
        self._session_key = msg[: self._session_key_length]
        self._server_salt = msg[
            self._session_key_length : self._session_key_length + self._salt_length
        ]
        passwd_hash = PasswordHash.generate_password_hash(login, password).encode()
        salt = self._server_salt

        hasher = hmac.new(passwd_hash, salt, self._digest_hash_name)
        digest = hasher.digest()
        res = binascii.b2a_base64(digest).decode()
        return res

    def encrypt_e2e(self, msg: str, receiver_key: str) -> str:
        """Зашифровать сообщение открытым ключом получателя"""
        msgb = self._prepare_to_encrypt(msg.encode())
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(receiver_key))
        res_bin = cipher_rsa.encrypt(msgb)
        res = self.e2e_prefix + binascii.b2a_base64(res_bin)
        return res.decode("ascii")

    def decrypt_e2e(self, msg: str) -> str:
        """Расшифровать сообщение закрытым ключом получателя"""
        msg_bin = binascii.a2b_base64(msg.encode("ascii")[self.e2e_prefix_len :])
        msg_decrypted = self._cipher_rsa.decrypt(msg_bin)
        msgb = self._prepare_after_decrypt(msg_decrypted)
        return msgb.decode()


class ServerSecurity(TranportEncryption):
    """Класс для обеспечения безопасности со стороны скрвера"""

    def __init__(self, message_step1: str) -> None:
        super().__init__()
        self._session_key = get_random_bytes(self._session_key_length)
        self._server_salt = get_random_bytes(self._salt_length)
        self.client_key = RSA.import_key(message_step1)
        self._cipher_rsa = PKCS1_OAEP.new(self.client_key)

    def process_auth_step2(self) -> str:
        """2 шаг аутентификации клиента на сервере"""
        msg = self._prepare_to_encrypt(self._session_key + self._server_salt)
        res_bin = self._cipher_rsa.encrypt(msg)
        res = binascii.b2a_base64(res_bin).decode()
        return res

    def process_auth_step4(self, message_step3: str, password_db_hash: str) -> None:
        """4 шаг аутентификации клиента на сервере"""
        salt = self._server_salt

        hasher = hmac.new(password_db_hash.encode(), salt, self._digest_hash_name)
        digest = hasher.digest()

        client_digest = binascii.a2b_base64(message_step3.encode())
        if hmac.compare_digest(digest, client_digest):
            return
        raise TransportSecurityAuthError
