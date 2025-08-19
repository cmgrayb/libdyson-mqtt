"""Exceptions for the libdyson_mqtt library."""

from typing import Optional


class DysonMqttError(Exception):
    """Base exception for all Dyson MQTT errors."""

    pass


class ConnectionError(DysonMqttError):
    """Raised when there's a connection error with the MQTT broker."""

    def __init__(self, message: str, error_code: Optional[int] = None) -> None:
        """Initialize the connection error.

        Args:
            message: Error message describing the connection issue
            error_code: Optional MQTT error code
        """
        super().__init__(message)
        self.error_code = error_code


class AuthenticationError(DysonMqttError):
    """Raised when authentication fails."""

    pass


class TopicError(DysonMqttError):
    """Raised when there's an issue with topic subscription or publishing."""

    pass


class ClientNotConnectedError(DysonMqttError):
    """Raised when trying to perform operations on a disconnected client."""

    pass


class CleanupError(DysonMqttError):
    """Raised when there's an error during client cleanup."""

    pass
