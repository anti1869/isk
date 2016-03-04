"""
Custom exceptions
"""


class IskException(Exception):
    """Base class for all Isk-related exceptions"""


class ImageDBException(IskException):
    """Problem with image db storage"""


class IskHttpServerException(IskException):
    """Problem with http server"""
