"""Утилиты для обеспечения безопасности"""
import binascii
import hashlib


class PasswordHash:
    """Генерация хеша для пароля пользователя"""

    _password_hash_name = "sha512"

    @staticmethod
    def generate_password_hash(login: str, password: str) -> str:
        """Сгенерировать хеш пароля пользователя"""
        salt = login.lower() + login.upper()
        passwd_hash = hashlib.pbkdf2_hmac(
            hash_name=PasswordHash._password_hash_name,
            password=password.encode(),
            salt=salt.encode(),
            iterations=10000,
        )
        return binascii.hexlify(passwd_hash).decode()
