"""Models for the libdyson_mqtt library."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class MqttMessage:
    """Represents an MQTT message received from a Dyson device."""

    topic: str
    payload: bytes
    qos: int
    retain: bool
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Ensure timestamp is set if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def payload_str(self) -> str:
        """Get the payload as a UTF-8 decoded string."""
        return self.payload.decode("utf-8", errors="replace")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "topic": self.topic,
            "payload": self.payload_str,
            "qos": self.qos,
            "retain": self.retain,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class ConnectionConfig:
    """Configuration for connecting to a Dyson device's MQTT broker."""

    host: str
    mqtt_username: str
    mqtt_password: str
    mqtt_topics: list[str]
    port: int = 1883
    keepalive: int = 60
    client_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not self.host:
            raise ValueError("Host cannot be empty")
        if not self.mqtt_username:
            raise ValueError("MQTT username cannot be empty")
        if not self.mqtt_password:
            raise ValueError("MQTT password cannot be empty")
        if not self.mqtt_topics:
            raise ValueError("MQTT topics list cannot be empty")
        if self.port < 1 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        if self.keepalive < 1:
            raise ValueError("Keepalive must be positive")


@dataclass
class ConnectionStatus:
    """Represents the current connection status."""

    connected: bool
    last_connect_time: Optional[datetime] = None
    last_disconnect_time: Optional[datetime] = None
    connection_attempts: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary."""
        return {
            "connected": self.connected,
            "last_connect_time": self.last_connect_time.isoformat() if self.last_connect_time else None,
            "last_disconnect_time": self.last_disconnect_time.isoformat() if self.last_disconnect_time else None,
            "connection_attempts": self.connection_attempts,
            "last_error": self.last_error,
        }
