
class UtilsTrSecurityError(Exception):
    def __str__(self):
        return f'Transport security error'


class UtilsSecurityNoSessionKeyError(UtilsTrSecurityError):
    def __str__(self):
        return f'Message cannon be en(de)crypted'


class UtilsSecurityValidationError(UtilsTrSecurityError):
    def __str__(self):
        return f'Message and key do not match'


class UtilsSecurityAuthError(Exception):
    def __str__(self):
        return f'Authorization error'
