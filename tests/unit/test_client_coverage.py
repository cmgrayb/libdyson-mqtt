"""Additional unit tests to improve code coverage."""

from unittest.mock import Mock, patch

import paho.mqtt.client as mqtt
import pytest

from libdyson_mqtt import ConnectionConfig, DysonMqttClient
from libdyson_mqtt.exceptions import CleanupError, ConnectionError, TopicError


class TestDysonMqttClientCoverage:
    """Additional tests to improve code coverage."""

    def test_connection_callback_with_success(self, sample_config: ConnectionConfig) -> None:
        """Test connection callback is called on successful connection."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)
            callback = Mock()
            client.set_connection_callback(callback)

            # Simulate successful connection
            client._on_connect(mock_client_instance, None, {}, mqtt.CONNACK_ACCEPTED)

            # Verify callback was called with success
            callback.assert_called_once_with(True, None)

    def test_connection_callback_with_failure(self, sample_config: ConnectionConfig) -> None:
        """Test connection callback is called on connection failure."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)
            callback = Mock()
            client.set_connection_callback(callback)

            # Simulate connection failure
            client._on_connect(mock_client_instance, None, {}, mqtt.CONNACK_REFUSED_NOT_AUTHORIZED)

            # Verify callback was called with failure (using the actual error message)
            expected_msg = "Failed to connect to MQTT broker: Connection Refused: not authorised."
            callback.assert_called_once_with(False, expected_msg)

    def test_connection_callback_exception_handling(self, sample_config: ConnectionConfig) -> None:
        """Test that exceptions in connection callbacks are handled gracefully."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)

            # Create a callback that raises an exception
            callback = Mock(side_effect=Exception("Callback error"))
            client.set_connection_callback(callback)

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                # Simulate successful connection - should handle callback exception
                client._on_connect(mock_client_instance, None, {}, mqtt.CONNACK_ACCEPTED)

                # Verify error was logged
                mock_logger.error.assert_called_with("Error in connection callback: Callback error")

    def test_message_callback_exception_handling(self, sample_config: ConnectionConfig) -> None:
        """Test that exceptions in message callbacks are handled gracefully."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)

            # Create a callback that raises an exception
            callback = Mock(side_effect=Exception("Message callback error"))
            client.set_message_callback(callback)

            # Create a mock MQTT message
            mock_msg = Mock()
            mock_msg.topic = "test/topic"
            mock_msg.payload = b"test payload"
            mock_msg.qos = 1

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                # Simulate message arrival - should handle callback exception
                client._on_message(mock_client_instance, None, mock_msg)

                # Verify error was logged
                mock_logger.error.assert_called_with("Error in message callback: Message callback error")

    def test_on_disconnect_with_unexpected_disconnect(self, sample_config: ConnectionConfig) -> None:
        """Test disconnect handler with unexpected disconnection."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)
            callback = Mock()
            client.set_connection_callback(callback)

            # Set initial connection status
            client._status.connected = True

            # Simulate unexpected disconnect (non-zero return code)
            client._on_disconnect(mock_client_instance, None, 1)

            # Verify status updated and callback called
            assert not client._status.connected
            assert client._status.last_error == "Unexpected disconnection: 1"
            callback.assert_called_once_with(False, "Unexpected disconnection: 1")

    def test_on_disconnect_callback_exception(self, sample_config: ConnectionConfig) -> None:
        """Test disconnect callback exception handling."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            client = DysonMqttClient(sample_config)

            # Create a callback that raises an exception
            callback = Mock(side_effect=Exception("Disconnect callback error"))
            client.set_connection_callback(callback)

            client._status.connected = True

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                # Simulate unexpected disconnect
                client._on_disconnect(mock_client_instance, None, 1)

                # Verify error was logged
                mock_logger.error.assert_called_with("Error in connection callback: Disconnect callback error")

    def test_subscribe_topics_when_not_connected(self, sample_config: ConnectionConfig) -> None:
        """Test subscribing to topics when not connected."""
        client = DysonMqttClient(sample_config)

        # Ensure client is not connected
        assert not client.is_connected()

        # Should return early without subscribing to any topics
        with patch.object(client._client, "subscribe") as mock_subscribe:
            client._subscribe_to_topics()

            # Should not have called subscribe since not connected
            mock_subscribe.assert_not_called()

    def test_subscribe_topics_with_errors(self, sample_config: ConnectionConfig) -> None:
        """Test topic subscription error handling."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock subscribe to return error
            mock_client_instance.subscribe.return_value = (mqtt.MQTT_ERR_NO_CONN, 1)

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                client._subscribe_to_topics()

                # Should log error for each topic
                assert mock_logger.error.call_count >= 1

    def test_subscribe_topics_with_exception(self, sample_config: ConnectionConfig) -> None:
        """Test topic subscription with exception."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock subscribe to raise exception
            mock_client_instance.subscribe.side_effect = Exception("Subscribe error")

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                client._subscribe_to_topics()

                # Should log error for exception
                mock_logger.error.assert_called()

    def test_connect_with_exception(self, sample_config: ConnectionConfig) -> None:
        """Test connect method when client setup fails."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock connect_async to raise exception
            mock_client_instance.connect_async.side_effect = Exception("Connection setup failed")

            client = DysonMqttClient(sample_config)

            with pytest.raises(ConnectionError, match="Failed to initiate connection"):
                client.connect()

    def test_disconnect_with_exception(self, sample_config: ConnectionConfig) -> None:
        """Test disconnect method when disconnection fails."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock disconnect to raise exception
            mock_client_instance.disconnect.side_effect = Exception("Disconnect failed")

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            with pytest.raises(CleanupError, match="Error during disconnect"):
                client.disconnect()

    def test_publish_with_mqtt_error(self, sample_config: ConnectionConfig) -> None:
        """Test publish method when MQTT publish fails."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock publish to return error
            mock_client_instance.publish.return_value = (mqtt.MQTT_ERR_NO_CONN, 1)

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            with pytest.raises(TopicError, match="Failed to publish to topic"):
                client.publish("test/topic", "test message")

    def test_publish_with_exception(self, sample_config: ConnectionConfig) -> None:
        """Test publish method when an exception occurs."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock publish to raise exception
            mock_client_instance.publish.side_effect = Exception("Publish failed")

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            with pytest.raises(TopicError, match="Error publishing to topic"):
                client.publish("test/topic", "test message")

    def test_on_message_processing_error(self, sample_config: ConnectionConfig) -> None:
        """Test message processing error handling."""
        client = DysonMqttClient(sample_config)

        # Create a malformed message that will cause processing error
        mock_msg = Mock()
        mock_msg.topic = "test/topic"
        mock_msg.payload = b"test payload"
        mock_msg.qos = 1

        with patch("libdyson_mqtt.client.MqttMessage") as mock_mqtt_message:
            # Make MqttMessage constructor raise an exception
            mock_mqtt_message.side_effect = Exception("Message creation failed")

            with patch("libdyson_mqtt.client.logger") as mock_logger:
                client._on_message(Mock(), None, mock_msg)

                # Should log the processing error
                mock_logger.error.assert_called_with("Error processing message: Message creation failed")

    def test_on_subscribe_callback(self, sample_config: ConnectionConfig) -> None:
        """Test subscription confirmation callback."""
        client = DysonMqttClient(sample_config)

        with patch("libdyson_mqtt.client.logger") as mock_logger:
            client._on_subscribe(Mock(), None, 123, [0, 1, 2])

            # Should log subscription confirmation
            mock_logger.debug.assert_called_with("Subscription confirmed (mid: 123, QoS: [0, 1, 2])")

    def test_on_publish_callback(self, sample_config: ConnectionConfig) -> None:
        """Test publish confirmation callback."""
        client = DysonMqttClient(sample_config)

        with patch("libdyson_mqtt.client.logger") as mock_logger:
            client._on_publish(Mock(), None, 456)

            # Should log publish confirmation
            mock_logger.debug.assert_called_with("Message published (mid: 456)")

    def test_on_log_warning_level(self, sample_config: ConnectionConfig) -> None:
        """Test MQTT log callback with warning level."""
        client = DysonMqttClient(sample_config)

        with patch("libdyson_mqtt.client.logger") as mock_logger:
            client._on_log(Mock(), None, mqtt.MQTT_LOG_WARNING, "Warning message")

            # Should log as warning
            mock_logger.warning.assert_called_with("MQTT: Warning message")

    def test_on_log_debug_level(self, sample_config: ConnectionConfig) -> None:
        """Test MQTT log callback with debug level."""
        client = DysonMqttClient(sample_config)

        with patch("libdyson_mqtt.client.logger") as mock_logger:
            client._on_log(Mock(), None, mqtt.MQTT_LOG_DEBUG, "Debug message")

            # Should log as debug
            mock_logger.debug.assert_called_with("MQTT: Debug message")

    def test_publish_with_bytes_payload(self, sample_config: ConnectionConfig) -> None:
        """Test publish method with bytes payload."""
        with patch("libdyson_mqtt.client.mqtt.Client") as mock_mqtt_client:
            mock_client_instance = Mock()
            mock_mqtt_client.return_value = mock_client_instance

            # Mock successful publish
            mock_client_instance.publish.return_value = (mqtt.MQTT_ERR_SUCCESS, 1)

            client = DysonMqttClient(sample_config)
            client._client = mock_client_instance
            client._status.connected = True

            # Test with bytes payload
            client.publish("test/topic", b"test bytes")

            # Should call publish with bytes
            mock_client_instance.publish.assert_called_once_with("test/topic", b"test bytes", 2, False)
