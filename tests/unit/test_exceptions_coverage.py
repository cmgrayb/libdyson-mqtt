"""Additional tests for exceptions to improve coverage."""

from libdyson_mqtt.exceptions import AuthenticationError, ConnectionError


class TestExceptionsCoverage:
    """Additional tests for exceptions coverage."""

    def test_connection_error_with_error_code(self) -> None:
        """Test ConnectionError with error code."""
        error = ConnectionError("Connection failed", error_code=5)

        assert str(error) == "Connection failed"
        assert error.error_code == 5

    def test_authentication_error(self) -> None:
        """Test AuthenticationError exception."""
        from libdyson_mqtt.exceptions import DysonMqttError

        error = AuthenticationError("Authentication failed")

        assert str(error) == "Authentication failed"
        assert isinstance(error, DysonMqttError)  # Should inherit from DysonMqttError
