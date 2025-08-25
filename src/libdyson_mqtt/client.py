"""MQTT client for communicating with Dyson devices."""

import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, List, Optional, Union

import paho.mqtt.client as mqtt
from paho.mqtt.client import ConnectFlags, DisconnectFlags
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from .exceptions import (
    ClientNotConnectedError,
    ConnectionError,
    TopicError,
)
from .models import ConnectionConfig, ConnectionStatus, MqttMessage

logger = logging.getLogger(__name__)


class DysonMqttClient:
    """Non-blocking MQTT client for Dyson devices."""

    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize the Dyson MQTT client.

        Args:
            config: Connection configuration for the Dyson device
        """
        self._config = config
        self._client_id = config.client_id or f"dyson-mqtt-{uuid.uuid4().hex[:8]}"
        self._client: Optional[mqtt.Client] = None
        self._status = ConnectionStatus(connected=False)
        self._lock = threading.Lock()

        # Callbacks
        self._message_callback: Optional[Callable[[MqttMessage], None]] = None
        self._connection_callback: Optional[Callable[[bool, Optional[str]], None]] = None

        # Message queue for non-blocking operations
        self._message_queue: List[MqttMessage] = []
        self._max_queue_size = 1000

        self._setup_client()

    def _setup_client(self) -> None:
        """Set up the MQTT client with callbacks."""
        self._client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=self._client_id)

        # Set credentials
        self._client.username_pw_set(self._config.mqtt_username, self._config.mqtt_password)

        # Set callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_subscribe = self._on_subscribe
        self._client.on_publish = self._on_publish
        self._client.on_log = self._on_log

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: ConnectFlags,
        reason_code: ReasonCode,
        properties: Optional[Properties] = None,
    ) -> None:
        """Handle connection events."""
        with self._lock:
            # Handle different types of reason codes
            if hasattr(reason_code, "is_failure"):
                # ReasonCode object (MQTT 5.0 style)
                is_failure = reason_code.is_failure
            else:
                # ConnackCode or integer (MQTT 3.1.1 style) - 0 means success
                is_failure = reason_code.value != 0 if hasattr(reason_code, "value") else reason_code != 0

            if is_failure:
                if hasattr(reason_code, "is_failure"):
                    # ReasonCode object - already has descriptive string representation
                    error_msg = f"Failed to connect to MQTT broker: {reason_code}"
                else:
                    # ConnackCode or integer - use connack_string for descriptive messages
                    code_value = reason_code.value if hasattr(reason_code, "value") else reason_code
                    error_msg = f"Failed to connect to MQTT broker: {mqtt.connack_string(code_value)}"
                logger.error(error_msg)
                self._status.connected = False
                self._status.last_error = error_msg
                self._status.connection_attempts += 1

                if self._connection_callback:
                    try:
                        self._connection_callback(False, error_msg)
                    except Exception as e:
                        logger.error(f"Error in connection callback: {e}")
            else:
                logger.info(f"Connected to MQTT broker at {self._config.host}")
                self._status.connected = True
                self._status.last_connect_time = datetime.now()
                self._status.last_error = None

                # Subscribe to all configured topics
                self._subscribe_to_topics()

                # Notify callback
                if self._connection_callback:
                    try:
                        self._connection_callback(True, None)
                    except Exception as e:
                        logger.error(f"Error in connection callback: {e}")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        disconnect_flags: DisconnectFlags,
        reason_code: ReasonCode,
        properties: Optional[Properties] = None,
    ) -> None:
        """Handle disconnection events."""
        with self._lock:
            logger.info(f"Disconnected from MQTT broker (reason: {reason_code})")
            self._status.connected = False
            self._status.last_disconnect_time = datetime.now()

            # Handle different types of reason codes
            if hasattr(reason_code, "is_failure"):
                # ReasonCode object (MQTT 5.0 style)
                is_failure = reason_code.is_failure
            else:
                # ConnackCode or integer - non-zero means failure/unexpected
                is_failure = reason_code.value != 0 if hasattr(reason_code, "value") else reason_code != 0

            if is_failure:
                error_msg = f"Unexpected disconnection: {reason_code}"
                self._status.last_error = error_msg
                logger.warning(error_msg)

                if self._connection_callback:
                    try:
                        self._connection_callback(False, error_msg)
                    except Exception as e:
                        logger.error(f"Error in connection callback: {e}")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Handle incoming messages."""
        try:
            # Create our message object
            dyson_msg = MqttMessage(
                topic=msg.topic,
                payload=msg.payload,
                qos=msg.qos,
                retain=msg.retain,
            )

            logger.debug(f"Received message on topic {msg.topic}: {dyson_msg.payload_str}")

            # Add to queue (non-blocking)
            with self._lock:
                if len(self._message_queue) >= self._max_queue_size:
                    # Remove oldest message to prevent memory issues
                    self._message_queue.pop(0)
                    logger.warning("Message queue full, dropped oldest message")

                self._message_queue.append(dyson_msg)

            # Call user callback if set
            if self._message_callback:
                try:
                    self._message_callback(dyson_msg)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _on_subscribe(
        self, client: mqtt.Client, userdata: Any, mid: int, reason_code_list: Any, properties: Any = None
    ) -> None:
        """Handle subscription confirmations."""
        logger.debug(f"Subscription confirmed (mid: {mid}, reason codes: {reason_code_list})")

    def _on_publish(
        self, client: mqtt.Client, userdata: Any, mid: int, reason_code: Any = None, properties: Any = None
    ) -> None:
        """Handle publish confirmations."""
        logger.debug(f"Message published (mid: {mid})")

    def _on_log(self, client: mqtt.Client, userdata: Any, level: int, buf: str) -> None:
        """Handle MQTT client logging."""
        if level <= mqtt.MQTT_LOG_WARNING:
            logger.warning(f"MQTT: {buf}")
        else:
            logger.debug(f"MQTT: {buf}")

    def _subscribe_to_topics(self) -> None:
        """Subscribe to all configured topics."""
        if not self._client or not self._status.connected:
            return

        for topic in self._config.mqtt_topics:
            try:
                result, mid = self._client.subscribe(topic, qos=2)  # QoS 2 for exactly once delivery
                if result != mqtt.MQTT_ERR_SUCCESS:
                    logger.error(f"Failed to subscribe to topic {topic}: {mqtt.error_string(result)}")
                else:
                    logger.info(f"Subscribed to topic: {topic}")
            except Exception as e:
                logger.error(f"Error subscribing to topic {topic}: {e}")

    def connect(self) -> None:
        """Connect to the MQTT broker (non-blocking).

        Raises:
            ConnectionError: If the connection attempt fails
        """
        if not self._client:
            raise ConnectionError("MQTT client not initialized")

        with self._lock:
            if self._status.connected:
                logger.warning("Already connected to MQTT broker")
                return

            try:
                logger.info(f"Connecting to MQTT broker at {self._config.host}:{self._config.port}")
                self._client.connect_async(self._config.host, self._config.port, self._config.keepalive)

                # Start the network loop in a separate thread
                self._client.loop_start()

            except Exception as e:
                error_msg = f"Failed to initiate connection: {e}"
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e

    def disconnect(self, timeout: float = 3.0) -> None:
        """Cleanly disconnect from the MQTT broker with timeout.

        Args:
            timeout: Maximum time to wait for disconnect (seconds)

        Raises:
            CleanupError: If the disconnection fails critically
        """
        if not self._client:
            return

        try:
            with self._lock:
                if self._status.connected:
                    logger.info("Disconnecting from MQTT broker")
                    self._client.disconnect()

                    # Wait for disconnect with timeout
                    start_time = time.time()
                    while self._status.connected and (time.time() - start_time) < timeout:
                        time.sleep(0.1)  # Short sleep to allow disconnect processing

                    if self._status.connected:
                        logger.warning(f"Disconnect timed out after {timeout}s, forcing cleanup")
                        self._status.connected = False  # Force status update

                # Stop the network loop
                self._client.loop_stop()

        except Exception as e:
            error_msg = f"Error during disconnect: {e}"
            logger.error(error_msg)
            # Don't raise the exception in normal cases - just log it
            # This prevents Home Assistant integration reload from hanging
            logger.warning("Continuing cleanup despite disconnect error")

    def publish(self, topic: str, payload: Union[str, bytes], qos: int = 2, retain: bool = False) -> None:
        """Publish a message to a topic (non-blocking).

        Args:
            topic: The MQTT topic to publish to
            payload: The message payload
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether the message should be retained by the broker

        Raises:
            ClientNotConnectedError: If not connected to the broker
            TopicError: If the publish fails
        """
        if not self._client:
            raise ClientNotConnectedError("MQTT client not initialized")

        with self._lock:
            if not self._status.connected:
                raise ClientNotConnectedError("Not connected to MQTT broker")

        try:
            if isinstance(payload, str):
                payload = payload.encode("utf-8")

            result, mid = self._client.publish(topic, payload, qos, retain)

            if result != mqtt.MQTT_ERR_SUCCESS:
                error_msg = f"Failed to publish to topic {topic}: {mqtt.error_string(result)}"
                logger.error(error_msg)
                raise TopicError(error_msg)
            else:
                logger.debug(f"Published message to topic {topic} (mid: {mid})")

        except Exception as e:
            if isinstance(e, (ClientNotConnectedError, TopicError)):
                raise
            error_msg = f"Error publishing to topic {topic}: {e}"
            logger.error(error_msg)
            raise TopicError(error_msg) from e

    def get_messages(self, clear_queue: bool = True) -> List[MqttMessage]:
        """Get all queued messages (non-blocking).

        Args:
            clear_queue: Whether to clear the internal queue after retrieval

        Returns:
            List of received MQTT messages
        """
        with self._lock:
            messages = self._message_queue.copy()
            if clear_queue:
                self._message_queue.clear()
            return messages

    def set_message_callback(self, callback: Optional[Callable[[MqttMessage], None]]) -> None:
        """Set callback for received messages.

        Args:
            callback: Function to call when a message is received, or None to clear
        """
        self._message_callback = callback

    def set_connection_callback(self, callback: Optional[Callable[[bool, Optional[str]], None]]) -> None:
        """Set callback for connection status changes.

        Args:
            callback: Function to call on connection changes (connected, error_msg), or None to clear
        """
        self._connection_callback = callback

    def get_status(self) -> ConnectionStatus:
        """Get current connection status.

        Returns:
            Current connection status
        """
        with self._lock:
            return ConnectionStatus(
                connected=self._status.connected,
                last_connect_time=self._status.last_connect_time,
                last_disconnect_time=self._status.last_disconnect_time,
                connection_attempts=self._status.connection_attempts,
                last_error=self._status.last_error,
            )

    def is_connected(self) -> bool:
        """Check if currently connected to the MQTT broker.

        Returns:
            True if connected, False otherwise
        """
        with self._lock:
            return self._status.connected

    def __enter__(self) -> "DysonMqttClient":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.disconnect()
