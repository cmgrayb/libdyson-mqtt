"""Unit tests for the models module."""

from datetime import datetime

import pytest

from libdyson_mqtt.models import ConnectionConfig, ConnectionStatus, MqttMessage


class TestConnectionConfig:
    """Tests for ConnectionConfig model."""

    def test_valid_config_creation(self) -> None:
        """Test creating a valid connection configuration."""
        config = ConnectionConfig(
            host="192.168.1.100",
            mqtt_username="test_user",
            mqtt_password="test_pass",
            mqtt_topics=["topic1", "topic2"],
            port=1883,
            keepalive=60,
        )

        assert config.host == "192.168.1.100"
        assert config.mqtt_username == "test_user"
        assert config.mqtt_password == "test_pass"
        assert config.mqtt_topics == ["topic1", "topic2"]
        assert config.port == 1883
        assert config.keepalive == 60

    def test_invalid_empty_host(self) -> None:
        """Test that empty host raises ValueError."""
        with pytest.raises(ValueError, match="Host cannot be empty"):
            ConnectionConfig(host="", mqtt_username="test_user", mqtt_password="test_pass", mqtt_topics=["topic1"])

    def test_invalid_empty_username(self) -> None:
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="MQTT username cannot be empty"):
            ConnectionConfig(host="192.168.1.100", mqtt_username="", mqtt_password="test_pass", mqtt_topics=["topic1"])

    def test_invalid_empty_password(self) -> None:
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="MQTT password cannot be empty"):
            ConnectionConfig(host="192.168.1.100", mqtt_username="test_user", mqtt_password="", mqtt_topics=["topic1"])

    def test_invalid_empty_topics(self) -> None:
        """Test that empty topics list raises ValueError."""
        with pytest.raises(ValueError, match="MQTT topics list cannot be empty"):
            ConnectionConfig(host="192.168.1.100", mqtt_username="test_user", mqtt_password="test_pass", mqtt_topics=[])

    def test_invalid_port_range(self) -> None:
        """Test that invalid port ranges raise ValueError."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            ConnectionConfig(
                host="192.168.1.100",
                mqtt_username="test_user",
                mqtt_password="test_pass",
                mqtt_topics=["topic1"],
                port=0,
            )

        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            ConnectionConfig(
                host="192.168.1.100",
                mqtt_username="test_user",
                mqtt_password="test_pass",
                mqtt_topics=["topic1"],
                port=65536,
            )

    def test_invalid_keepalive(self) -> None:
        """Test that invalid keepalive raises ValueError."""
        with pytest.raises(ValueError, match="Keepalive must be positive"):
            ConnectionConfig(
                host="192.168.1.100",
                mqtt_username="test_user",
                mqtt_password="test_pass",
                mqtt_topics=["topic1"],
                keepalive=0,
            )


class TestMqttMessage:
    """Tests for MqttMessage model."""

    def test_message_creation_with_timestamp(self) -> None:
        """Test creating a message with explicit timestamp."""
        timestamp = datetime.now()
        msg = MqttMessage(topic="test/topic", payload=b"test payload", qos=2, retain=False, timestamp=timestamp)

        assert msg.topic == "test/topic"
        assert msg.payload == b"test payload"
        assert msg.qos == 2
        assert msg.retain is False
        assert msg.timestamp == timestamp

    def test_message_creation_without_timestamp(self) -> None:
        """Test creating a message without explicit timestamp."""
        msg = MqttMessage(topic="test/topic", payload=b"test payload", qos=2, retain=False)

        assert msg.topic == "test/topic"
        assert msg.payload == b"test payload"
        assert msg.qos == 2
        assert msg.retain is False
        assert msg.timestamp is not None
        assert isinstance(msg.timestamp, datetime)

    def test_payload_str_property(self) -> None:
        """Test the payload_str property."""
        msg = MqttMessage(topic="test/topic", payload=b"test payload", qos=2, retain=False)

        assert msg.payload_str == "test payload"

    def test_payload_str_with_invalid_utf8(self) -> None:
        """Test payload_str with invalid UTF-8 bytes."""
        msg = MqttMessage(topic="test/topic", payload=b"\xff\xfe", qos=2, retain=False)  # Invalid UTF-8

        # Should not raise exception, uses 'replace' error handling
        payload_str = msg.payload_str
        assert isinstance(payload_str, str)

    def test_to_dict(self) -> None:
        """Test converting message to dictionary."""
        timestamp = datetime.now()
        msg = MqttMessage(topic="test/topic", payload=b"test payload", qos=2, retain=True, timestamp=timestamp)

        result = msg.to_dict()
        expected = {
            "topic": "test/topic",
            "payload": "test payload",
            "qos": 2,
            "retain": True,
            "timestamp": timestamp.isoformat(),
        }

        assert result == expected

    def test_to_dict_without_timestamp(self) -> None:
        """Test converting message without timestamp to dictionary."""
        msg = MqttMessage(topic="test/topic", payload=b"test payload", qos=2, retain=True)

        result = msg.to_dict()
        assert result["topic"] == "test/topic"
        assert result["payload"] == "test payload"
        assert result["qos"] == 2
        assert result["retain"] is True
        assert result["timestamp"] is not None


class TestConnectionStatus:
    """Tests for ConnectionStatus model."""

    def test_status_creation(self) -> None:
        """Test creating connection status."""
        status = ConnectionStatus(connected=True)

        assert status.connected is True
        assert status.last_connect_time is None
        assert status.last_disconnect_time is None
        assert status.connection_attempts == 0
        assert status.last_error is None

    def test_status_to_dict(self) -> None:
        """Test converting status to dictionary."""
        connect_time = datetime.now()
        status = ConnectionStatus(
            connected=True, last_connect_time=connect_time, connection_attempts=3, last_error="Test error"
        )

        result = status.to_dict()
        expected = {
            "connected": True,
            "last_connect_time": connect_time.isoformat(),
            "last_disconnect_time": None,
            "connection_attempts": 3,
            "last_error": "Test error",
        }

        assert result == expected
