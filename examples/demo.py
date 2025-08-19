#!/usr/bin/env python3
"""Simple example demonstrating libdyson-mqtt functionality."""

import logging
import time
from typing import Optional

from libdyson_mqtt import ConnectionConfig, DysonMqttClient, MqttMessage

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)


def create_test_client() -> DysonMqttClient:
    """Create a test client with example configuration."""
    config = ConnectionConfig(
        host="192.168.1.100",  # Replace with your Dyson device IP
        mqtt_username="475",  # Replace with your device serial/username
        mqtt_password="your_device_password",  # Replace with your device password
        mqtt_topics=["475/device/status", "475/device/command", "475/device/faults"],  # Replace with your device topics
        port=1883,
        keepalive=60,
        client_id="test-client",
    )

    return DysonMqttClient(config)


def demo_basic_usage() -> None:
    """Demonstrate basic usage patterns."""
    print("libdyson-mqtt Demo")
    print("==================")

    client = create_test_client()

    print("1. Basic connection and status check")
    print(f"   Initial status: Connected = {client.is_connected()}")

    try:
        # Connect (this is non-blocking)
        client.connect()
        print("   Connection initiated...")

        # Give it a moment to connect (in real usage, use callbacks)
        time.sleep(2)

        print(f"   Status after connect: Connected = {client.is_connected()}")

        if client.is_connected():
            print("   ✓ Connected successfully!")

            # Demonstrate publishing
            print("\\n2. Publishing a message")
            try:
                client.publish("475/device/command", '{"msg": "REQUEST-CURRENT-STATE"}')
                print("   ✓ Message published")
            except Exception as e:
                print(f"   ✗ Publish failed: {e}")

            # Check for any received messages
            print("\\n3. Checking for received messages")
            messages = client.get_messages()
            print(f"   Found {len(messages)} messages in queue")

            for i, msg in enumerate(messages, 1):
                print(f"   Message {i}:")
                print(f"     Topic: {msg.topic}")
                print(f"     Payload: {msg.payload_str}")
                print(f"     QoS: {msg.qos}")
        else:
            print("   ✗ Connection failed")
            status = client.get_status()
            print(f"   Error: {status.last_error}")

    finally:
        print("\\n4. Cleaning up")
        client.disconnect()
        print("   ✓ Disconnected cleanly")


def demo_callbacks() -> None:
    """Demonstrate callback functionality."""
    print("\\n\\nCallback Demo")
    print("=============")

    received_messages = []
    connection_events = []

    def on_message(message: MqttMessage) -> None:
        """Handle received messages."""
        print(f"📨 Message received: {message.topic} -> {message.payload_str[:50]}...")
        received_messages.append(message)

    def on_connection_change(connected: bool, error: Optional[str]) -> None:
        """Handle connection status changes."""
        if connected:
            print("🔗 Connected to device!")
        else:
            print(f"❌ Connection lost: {error}")
        connection_events.append((connected, error))

    client = create_test_client()
    client.set_message_callback(on_message)
    client.set_connection_callback(on_connection_change)

    try:
        print("Connecting with callbacks enabled...")
        client.connect()

        # Wait for connection and any initial messages
        time.sleep(5)

        if client.is_connected():
            # Send a command to generate some traffic
            client.publish("475/device/command", '{"msg": "REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA"}')

            # Wait for responses
            time.sleep(3)

        print(f"\\nReceived {len(received_messages)} messages via callbacks")
        print(f"Connection events: {len(connection_events)}")

    finally:
        client.disconnect()


def demo_context_manager() -> None:
    """Demonstrate context manager usage."""
    print("\\n\\nContext Manager Demo")
    print("====================")

    config = ConnectionConfig(
        host="192.168.1.100",
        mqtt_username="475",
        mqtt_password="your_device_password",
        mqtt_topics=["475/device/status"],
    )

    try:
        # Context manager automatically handles connection/disconnection
        with DysonMqttClient(config) as client:
            print("✓ Connected via context manager")

            # Use the client
            client.publish("475/device/command", '{"msg": "REQUEST-CURRENT-STATE"}')
            time.sleep(2)

            messages = client.get_messages()
            print(f"Received {len(messages)} messages")

    except Exception as e:
        print(f"Error: {e}")

    print("✓ Context manager automatically disconnected")


def main() -> None:
    """Run all demos."""
    print("This demo shows libdyson-mqtt functionality.")
    print("Note: You'll need to update the configuration with your device details.\\n")

    try:
        demo_basic_usage()
        demo_callbacks()
        demo_context_manager()

    except KeyboardInterrupt:
        print("\\n\\nDemo interrupted by user")
    except Exception as e:
        print(f"\\n\\nDemo failed: {e}")
        print("Make sure to update the connection configuration with your device details!")

    print("\\n\\nDemo complete!")


if __name__ == "__main__":
    main()
