"""Unit tests for the client module."""

from unittest.mock import Mock, patch

import pytest

from libdyson_mqtt import ConnectionConfig, DysonMqttClient
from libdyson_mqtt.exceptions import ClientNotConnectedError


class TestDysonMqttClient:
    """Tests for DysonMqttClient."""

    def test_client_initialization(self, sample_config: ConnectionConfig) -> None:
        """Test client initialization."""
        client = DysonMqttClient(sample_config)

        assert not client.is_connected()
        assert client._config == sample_config

    def test_context_manager(self, sample_config: ConnectionConfig) -> None:
        """Test client as context manager."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Test context manager entry and exit
            with DysonMqttClient(sample_config) as client:
                assert client is not None

    def test_publish_when_not_connected(self, sample_config: ConnectionConfig) -> None:
        """Test publishing when not connected raises exception."""
        client = DysonMqttClient(sample_config)

        with pytest.raises(ClientNotConnectedError):
            client.publish("test/topic", "test payload")

    def test_get_messages(self, sample_config: ConnectionConfig) -> None:
        """Test getting messages from queue."""
        client = DysonMqttClient(sample_config)

        messages = client.get_messages()
        assert messages == []

    def test_connection_callbacks(self, sample_config: ConnectionConfig) -> None:
        """Test setting connection callbacks."""
        client = DysonMqttClient(sample_config)

        # Test setting message callback
        callback = Mock()
        client.set_message_callback(callback)
        assert client._message_callback == callback

        # Test setting connection callback
        conn_callback = Mock()
        client.set_connection_callback(conn_callback)
        assert client._connection_callback == conn_callback

        # Test clearing message callback
        client.set_message_callback(None)
        assert client._message_callback is None

    def test_clear_connection_callback(self, sample_config: ConnectionConfig) -> None:
        """Test clearing connection callback."""
        client = DysonMqttClient(sample_config)

        # Set a callback first
        callback = Mock()
        client.set_connection_callback(callback)
        assert client._connection_callback == callback

        # Clear the callback
        client.set_connection_callback(None)
        assert client._connection_callback is None
