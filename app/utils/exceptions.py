class CustomTokenExceptionBase(Exception):
    def init(self, detail: str):
        self.detail = detail


class CredentialsException(CustomTokenExceptionBase):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class TokenExpiredException(CustomTokenExceptionBase):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class GenerateReferralCodeException(Exception):
    def __init__(self, message="Unable to generate unique referral code after multiple attempts."):
        self.message = message
        super().__init__(self.message)


class TokenError(CustomTokenExceptionBase):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)



