"""
**File:** ``test_linked_service.py``
**Region:** ``tests/linked_service/unit_tests``

Unit tests for TicketcoLinkedService.

Covers:
- type property returns the correct resource type.
- Service initialises without error given valid settings.
"""

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
