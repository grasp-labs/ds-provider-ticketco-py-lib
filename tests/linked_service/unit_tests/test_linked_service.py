"""
**File:** ``test_linked_service.py``
**Region:** ``tests/linked_service/unit_tests``

Unit tests for TicketcoLinkedService.

Covers:
- type property returns the correct resource type.
- Service initialises without error given valid settings.
- connect() and test_connection() methods.
"""

from unittest.mock import MagicMock, PropertyMock, patch
from uuid import uuid4

from ds_provider_ticketco_py_lib.linked_service import (
    TicketcoLinkedService,
    TicketcoLinkedServiceSettings,
)


def make_settings():
    """Create TicketcoLinkedServiceSettings for testing."""
    return TicketcoLinkedServiceSettings(
        api_token="test_token",
        host="https://demo.ticketco.events",
    )


def make_service():
    """Create a TicketcoLinkedService for testing."""
    return TicketcoLinkedService(
        settings=make_settings(),
        id=uuid4(),
        name="test",
        version="1.0.0",
        description="desc",
    )


def test_type_property():
    """type property returns TICKETCO_LINKED_SERVICE."""
    service = make_service()
    assert service.type.name == "TICKETCO_LINKED_SERVICE"


def test_type_value():
    """type property value matches the expected resource kind string."""
    service = make_service()
    assert service.type == "DS.RESOURCE.LINKED_SERVICE.TICKETCO"


def test_service_initializes_without_error():
    """Service can be instantiated with valid settings."""
    service = make_service()
    assert service is not None


def test_settings_accessible_on_service():
    """Settings are accessible via the service instance."""
    service = make_service()
    assert service.settings.api_token == "test_token"
    assert service.settings.host == "https://demo.ticketco.events"


def test_connect_creates_connection():
    """connect() successfully creates a connection."""
    service = make_service()

    # Mock the parent class's connect method
    with patch("ds_protocol_http_py_lib.HttpLinkedService.connect") as mock_connect:
        service.connect()
        mock_connect.assert_called_once()


def test_test_connection_returns_true_on_success():
    """test_connection() returns (True, message) when connection succeeds."""
    service = make_service()

    # Mock successful connection test
    mock_connection = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_connection.get.return_value = mock_response

    with patch.object(
        type(service),
        "connection",
        new_callable=PropertyMock,
        return_value=mock_connection
    ):
        success, message = service.test_connection()

    assert success is True
    assert "successfully" in message.lower() or "connected" in message.lower()


def test_test_connection_returns_false_on_failure():
    """test_connection() returns (False, message) when connection fails."""
    service = make_service()

    # Mock failed connection test
    with patch.object(
        type(service),
        "connection",
        new_callable=PropertyMock,
        side_effect=Exception("Connection failed")
    ):
        success, message = service.test_connection()

    assert success is False
    assert "failed" in message.lower() or "error" in message.lower()
