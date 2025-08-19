"""Python library for MQTT communication with Dyson devices."""

from .client import DysonMqttClient
from .exceptions import (
    AuthenticationError,
    CleanupError,
    ClientNotConnectedError,
    ConnectionError,
    DysonMqttError,
    TopicError,
)
from .models import ConnectionConfig, ConnectionStatus, MqttMessage

__version__ = "0.1.0"
__all__ = [
    "DysonMqttClient",
    "ConnectionConfig",
    "ConnectionStatus",
    "MqttMessage",
    "DysonMqttError",
    "ConnectionError",
    "AuthenticationError",
    "TopicError",
    "ClientNotConnectedError",
    "CleanupError",
]
