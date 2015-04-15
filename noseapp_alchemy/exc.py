# -*- coding: utf-8 -*-


class BaseError(BaseException):
    pass


class NotFound(BaseError):
    pass


class InvalidBindKey(BaseError):
    pass
