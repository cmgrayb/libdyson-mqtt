# libdyson-mqtt

A Python library for MQTT communication with Dyson devices.

## Overview

`libdyson-mqtt` provides a clean, non-blocking interface for communicating with Dyson devices over MQTT. The library handles connection management, message queuing, and provides callbacks for real-time message processing.

## Features

- **Non-blocking operations**: All operations are asynchronous and won't block your application
- **Clean connection management**: Automatic connection handling with proper cleanup
- **Message queuing**: Messages are queued internally for processing
- **Callback support**: Real-time callbacks for messages and connection status
- **Type safety**: Full type annotations and mypy support
- **Comprehensive testing**: Unit and integration tests included

## Installation

```bash
pip install libdyson-mqtt
```

For development:

```bash
pip install -e .[dev]
```

## Quick Start

```python
from libdyson_mqtt import DysonMqttClient, ConnectionConfig

# Configure connection
config = ConnectionConfig(
    host="192.168.1.100",  # Your Dyson device IP
    mqtt_username="your_username",
    mqtt_password="your_password", 
    mqtt_topics=["475/device/status", "475/device/command"],
    port=1883,
    keepalive=60
)

# Create and connect client
client = DysonMqttClient(config)
client.connect()

# Check if connected
if client.is_connected():
    print("Connected successfully!")
    
    # Publish a command
    client.publish("475/device/command", '{"command": "status"}')
    
    # Get received messages
    messages = client.get_messages()
    for msg in messages:
        print(f"Topic: {msg.topic}, Payload: {msg.payload_str}")

# Clean disconnect
client.disconnect()
```

## Using Context Manager

For automatic connection management:

```python
from libdyson_mqtt import DysonMqttClient, ConnectionConfig

config = ConnectionConfig(
    host="192.168.1.100",
    mqtt_username="your_username",
    mqtt_password="your_password",
    mqtt_topics=["475/device/status", "475/device/command"]
)

# Automatically connects and disconnects
with DysonMqttClient(config) as client:
    client.publish("475/device/command", '{"command": "status"}')
    messages = client.get_messages()
```

## Using Callbacks

For real-time message processing:

```python
def on_message(message):
    print(f"Received: {message.topic} -> {message.payload_str}")

def on_connection_change(connected, error):
    if connected:
        print("Connected to device!")
    else:
        print(f"Connection lost: {error}")

client = DysonMqttClient(config)
client.set_message_callback(on_message)
client.set_connection_callback(on_connection_change)

client.connect()
# Messages will now be processed in real-time via callbacks
```

## API Reference

### ConnectionConfig

Configuration class for MQTT connection:

- `host`: IPv4 address or IPv6 .local DNS address
- `mqtt_username`: MQTT username  
- `mqtt_password`: MQTT password
- `mqtt_topics`: List of topics to subscribe to
- `port`: MQTT port (default: 1883)
- `keepalive`: Keep-alive interval in seconds (default: 60)
- `client_id`: Optional custom client ID

### DysonMqttClient

Main client class for MQTT communication:

#### Methods

- `connect()`: Connect to MQTT broker (non-blocking)
- `disconnect()`: Disconnect from broker
- `publish(topic, payload, qos=2, retain=False)`: Publish message
- `get_messages(clear_queue=True)`: Get queued messages
- `set_message_callback(callback)`: Set message received callback
- `set_connection_callback(callback)`: Set connection status callback
- `is_connected()`: Check connection status
- `get_status()`: Get detailed connection status

### MqttMessage

Represents a received MQTT message:

- `topic`: Message topic
- `payload`: Raw payload bytes
- `payload_str`: Payload as UTF-8 string
- `qos`: Quality of Service level
- `retain`: Whether message is retained
- `timestamp`: When message was received
- `to_dict()`: Convert to dictionary

## Error Handling

The library defines several exception types:

- `DysonMqttError`: Base exception
- `ConnectionError`: Connection issues
- `AuthenticationError`: Authentication failures  
- `TopicError`: Topic subscription/publishing issues
- `ClientNotConnectedError`: Operations on disconnected client
- `CleanupError`: Cleanup failures

```python
from libdyson_mqtt.exceptions import ConnectionError, ClientNotConnectedError

try:
    client.connect()
except ConnectionError as e:
    print(f"Failed to connect: {e}")

try:
    client.publish("test/topic", "message")
except ClientNotConnectedError:
    print("Not connected to broker")
```

## Development

Install development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Run type checking:

```bash
mypy src/
```

Format code:

```bash
black src/ tests/
isort src/ tests/
```

## Requirements

- Python 3.9+
- paho-mqtt >= 1.6.0

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests to the main repository.

## Home Assistant Integration

This library is designed to work well with Home Assistant integrations. The non-blocking design and callback system make it suitable for use in Home Assistant custom components:

```python
# In your Home Assistant integration
import asyncio
from libdyson_mqtt import DysonMqttClient, ConnectionConfig

class DysonDevice:
    def __init__(self, hass, config):
        self.hass = hass
        self.client = DysonMqttClient(config)
        self.client.set_message_callback(self._handle_message)
        
    def _handle_message(self, message):
        # Process device status updates
        self.hass.loop.call_soon_threadsafe(
            self._update_state, message
        )
        
    async def _update_state(self, message):
        # Update Home Assistant entity state
        pass
```
