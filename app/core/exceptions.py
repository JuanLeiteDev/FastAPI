class UserNotFoundError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class TwoFactorAuthNotConfiguredError(Exception):
    pass

class InvalidTwoFactorAuthCodeError(Exception):
    pass

class InvalidEmailOrPasswordError(Exception):
    pass

class EmailConfirmationRequiredError(Exception):
    pass

class TwoFactorAuthAlreadyConfiguredError(Exception):
    pass

class EmailAlreadyConfirmedError(Exception):
    pass

class InvalidEmailConfirmationCodeError(Exception):
    pass

class ExpiredEmailConfirmationCodeError(Exception):
    pass