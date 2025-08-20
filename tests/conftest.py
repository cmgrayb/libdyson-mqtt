"""Test fixtures for the test suite."""

import pytest

from libdyson_mqtt import ConnectionConfig


@pytest.fixture
def sample_config():
    """Provide a sample connection configuration for testing."""
    return ConnectionConfig(
        host="192.168.1.100",
        mqtt_username="test_user",
        mqtt_password="test_pass",
        mqtt_topics=["475/test/status", "475/test/command"],
        port=1883,
        keepalive=60,
        client_id="test_client",
    )
