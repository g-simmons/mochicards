class MochiError(Exception):
    """Base exception for all MochiClient related errors."""


class MochiAuthenticationError(MochiError):
    """Raised when there's an authentication-related issue."""


class MochiNotFoundError(MochiError):
    """Raised when a resource is not found."""
