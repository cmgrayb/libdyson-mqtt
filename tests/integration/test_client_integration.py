"""Integration tests for the DysonMqttClient.

These tests use a mock MQTT broker to test the full client functionality.
"""

import json
from typing import Optional
from unittest.mock import Mock, patch

import pytest

from libdyson_mqtt import ConnectionConfig, DysonMqttClient, MqttMessage


@pytest.fixture
def integration_config() -> ConnectionConfig:
    """Configuration for integration testing."""
    return ConnectionConfig(
        host="localhost",
        mqtt_username="test_user",
        mqtt_password="test_pass",
        mqtt_topics=["test/device/status", "test/device/command"],
        port=1883,
        keepalive=30,
        client_id="integration_test_client",
    )


class TestDysonMqttClientIntegration:
    """Integration tests for the complete client workflow."""

    def test_client_lifecycle(self, integration_config: ConnectionConfig) -> None:
        """Test the complete client lifecycle with mocked MQTT."""
        messages_received = []
        connection_events = []

        def message_callback(message: MqttMessage) -> None:
            messages_received.append(message)

        def connection_callback(connected: bool, error: Optional[str]) -> None:
            connection_events.append((connected, error))

        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            # Setup mock MQTT client
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock successful connection
            mock_client_instance.connect_async.return_value = 0

            # Mock subscribe and publish methods to return expected tuples
            mock_client_instance.subscribe.return_value = (0, 1)  # (result, mid)
            mock_client_instance.publish.return_value = (0, 1)  # (result, mid)

            # Mock publish and subscribe methods to return expected tuples
            import paho.mqtt.client as mqtt

            mock_client_instance.publish.return_value = (mqtt.MQTT_ERR_SUCCESS, 1)
            mock_client_instance.subscribe.return_value = (mqtt.MQTT_ERR_SUCCESS, 1)

            # Create client
            client = DysonMqttClient(integration_config)
            client.set_message_callback(message_callback)
            client.set_connection_callback(connection_callback)

            # Test connection
            client.connect()

            # Simulate successful connection
            client._on_connect(mock_client_instance, None, {}, 0)

            assert client.is_connected()

            # Verify subscriptions were attempted
            expected_calls = len(integration_config.mqtt_topics)
            assert mock_client_instance.subscribe.call_count == expected_calls

            # Simulate receiving a message
            mock_message = Mock()
            mock_message.topic = "test/device/status"
            mock_message.payload = b'{"status": "active", "temperature": 22.5}'
            mock_message.qos = 2
            mock_message.retain = False

            client._on_message(mock_client_instance, None, mock_message)

            # Verify message was processed
            assert len(messages_received) == 1
            received_msg = messages_received[0]
            assert received_msg.topic == "test/device/status"
            assert received_msg.payload_str == '{"status": "active", "temperature": 22.5}'

            # Test publishing
            client.publish("test/device/command", '{"command": "power_on"}')
            mock_client_instance.publish.assert_called_once()

            # Test clean disconnect
            client.disconnect()
            mock_client_instance.disconnect.assert_called_once()

    def test_message_queue_functionality(self, integration_config: ConnectionConfig) -> None:
        """Test message queuing without callbacks."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(integration_config)
            client.connect()
            client._on_connect(mock_client_instance, None, {}, 0)

            # Simulate multiple messages
            for i in range(3):
                mock_message = Mock()
                mock_message.topic = f"test/device/status/{i}"
                mock_message.payload = json.dumps({"msg_id": i}).encode()
                mock_message.qos = 2
                mock_message.retain = False

                client._on_message(mock_client_instance, None, mock_message)

            # Get messages from queue
            messages = client.get_messages()
            assert len(messages) == 3

            # Verify messages are in order
            for i, msg in enumerate(messages):
                assert msg.topic == f"test/device/status/{i}"
                payload_data = json.loads(msg.payload_str)
                assert payload_data["msg_id"] == i

            # Queue should be empty after retrieval
            messages = client.get_messages()
            assert len(messages) == 0

    def test_connection_error_handling(self, integration_config: ConnectionConfig) -> None:
        """Test handling of connection errors."""
        connection_events = []

        def connection_callback(connected: bool, error: Optional[str]) -> None:
            connection_events.append((connected, error))

        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(integration_config)
            client.set_connection_callback(connection_callback)

            client.connect()

            # Simulate connection failure
            client._on_connect(mock_client_instance, None, {}, 5)  # Connection refused

            assert not client.is_connected()

            # Verify error was captured
            status = client.get_status()
            assert not status.connected
            assert status.last_error is not None
            assert "Failed to connect" in status.last_error

    def test_message_queue_overflow(self, integration_config: ConnectionConfig) -> None:
        """Test message queue overflow handling."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(integration_config)
            client._max_queue_size = 5  # Set small queue for testing

            client.connect()
            client._on_connect(mock_client_instance, None, {}, 0)

            # Send more messages than queue can hold
            for i in range(10):
                mock_message = Mock()
                mock_message.topic = f"test/overflow/{i}"
                mock_message.payload = f"message_{i}".encode()
                mock_message.qos = 2
                mock_message.retain = False

                client._on_message(mock_client_instance, None, mock_message)

            # Should only have the last 5 messages (oldest dropped)
            messages = client.get_messages()
            assert len(messages) == 5

            # Should have messages 5-9 (0-4 were dropped)
            for i, msg in enumerate(messages):
                expected_id = i + 5
                assert msg.topic == f"test/overflow/{expected_id}"
                assert msg.payload_str == f"message_{expected_id}"
