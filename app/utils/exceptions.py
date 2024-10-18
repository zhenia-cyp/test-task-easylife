from http.client import HTTPException


class CustomTokenExceptionBase(Exception):
    """base exception class for custom
      token-related exceptions"""
    def init(self, detail: str):
        self.detail = detail


class CredentialsException(CustomTokenExceptionBase):
    """raised when there are credential-related issues"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class TokenExpiredException(CustomTokenExceptionBase):
    """raised when the token has expired"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class GenerateReferralCodeException(Exception):
    """raised when unable to generate a unique
    referral code after multiple attempts"""
    def __init__(self, message="Unable to generate unique referral code after multiple attempts."):
        self.message = message
        super().__init__(self.message)


class TokenError(CustomTokenExceptionBase):
    """raised for general token errors"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class TokenNotFoundException(HTTPException):
    """raised when the token is not found"""
    def __init__(self, detail: str = "Unauthorized: token not found"):
        super().__init__(401, detail)



