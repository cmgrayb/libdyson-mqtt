#!/usr/bin/env python3
"""Example usage of libdyson-mqtt library."""

import json
import time
from datetime import datetime

from libdyson_mqtt import ConnectionConfig, DysonMqttClient


def message_handler(message):
    """Handle incoming MQTT messages."""
    print(f"[{datetime.now().isoformat()}] Received message:")
    print(f"  Topic: {message.topic}")
    print(f"  Payload: {message.payload_str}")
    print(f"  QoS: {message.qos}")
    print(f"  Retained: {message.retain}")
    print("---")


def connection_handler(connected, error):
    """Handle connection status changes."""
    if connected:
        print("✓ Connected to Dyson device")
    else:
        print(f"✗ Connection lost: {error}")


def main():
    """Main example function."""
    # Example configuration - replace with your device details
    config = ConnectionConfig(
        host="192.168.1.100",  # Replace with your Dyson device IP
        mqtt_username="your_username",  # Replace with your username
        mqtt_password="your_password",  # Replace with your password
        mqtt_topics=[
            "475/your_device/status",  # Replace with your device serial
            "475/your_device/command",  # Replace with your device serial
            "475/your_device/faults",  # Replace with your device serial
        ],
        port=1883,
        keepalive=60,
        client_id="example-client",
    )

    print("libdyson-mqtt Example")
    print("====================")
    print(f"Connecting to {config.host}...")

    # Create client with callbacks
    client = DysonMqttClient(config)
    client.set_message_callback(message_handler)
    client.set_connection_callback(connection_handler)

    try:
        # Connect to device
        client.connect()

        # Wait a moment for connection to establish
        time.sleep(2)

        if client.is_connected():
            print("\\nSending status request...")

            # Example command to request status
            command = {"msg": "REQUEST-CURRENT-STATE", "time": datetime.now().isoformat()}

            client.publish("475/your_device/command", json.dumps(command))  # Replace with your device serial

            print("\\nListening for messages (press Ctrl+C to stop)...")

            # Listen for messages for 30 seconds
            start_time = time.time()
            while time.time() - start_time < 30:
                # Get any queued messages (in addition to callback)
                messages = client.get_messages()
                if messages:
                    print(f"Retrieved {len(messages)} messages from queue")

                time.sleep(1)

                # Show connection status
                status = client.get_status()
                if not status.connected:
                    print("Connection lost, attempting to reconnect...")
                    client.connect()
                    time.sleep(2)

        else:
            print("Failed to connect to device")
            return 1

    except KeyboardInterrupt:
        print("\\n\\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        print("\\nDisconnecting...")
        client.disconnect()
        print("Disconnected cleanly")

    return 0


def example_context_manager():
    """Example using context manager for automatic cleanup."""
    config = ConnectionConfig(
        host="192.168.1.100",
        mqtt_username="your_username",
        mqtt_password="your_password",
        mqtt_topics=["475/your_device/status"],
    )

    print("\\nContext Manager Example:")
    print("========================")

    # Using context manager - automatically connects and disconnects
    try:
        with DysonMqttClient(config) as client:
            print("Connected via context manager")

            # Send a command
            client.publish("475/your_device/command", '{"msg": "REQUEST-CURRENT-STATE"}')

            # Wait for responses
            time.sleep(5)

            # Get messages
            messages = client.get_messages()
            print(f"Received {len(messages)} messages")
            for msg in messages:
                print(f"  {msg.topic}: {msg.payload_str}")

    except Exception as e:
        print(f"Error in context manager example: {e}")

    print("Context manager automatically disconnected")


if __name__ == "__main__":
    exit_code = main()

    # Uncomment to run context manager example
    # example_context_manager()

    exit(exit_code)
