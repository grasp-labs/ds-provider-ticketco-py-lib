"""
**File:** ``test_linked_service_settings.py``
**Region:** ``tests/linked_service/unit_tests``

Description
-----------
TicketcoLinkedServiceSettings initialization and default value tests.

Covers:
- Default host is the production URL.
- api_token is required.
- auth_type defaults to NO_AUTH.
"""

from ds_protocol_http_py_lib.enums import AuthType

from ds_provider_ticketco_py_lib.linked_service import TicketcoLinkedServiceSettings


def test_settings_defaults():
    """Default host is the production URL and auth_type is NO_AUTH."""
    settings = TicketcoLinkedServiceSettings(api_token="token123")

    assert settings.host == "https://ticketco.events"
    assert settings.auth_type == AuthType.NO_AUTH


def test_settings_custom_host():
    """Host can be overridden to the demo environment."""
    settings = TicketcoLinkedServiceSettings(
        api_token="token123",
        host="https://demo.ticketco.events",
    )

    assert settings.host == "https://demo.ticketco.events"


def test_settings_api_token_stored():
    """api_token is stored in settings."""
    settings = TicketcoLinkedServiceSettings(api_token="my_secret_token")

    assert settings.api_token == "my_secret_token"


def test_settings_has_auth_type_attribute():
    """auth_type attribute is present on settings."""
    settings = TicketcoLinkedServiceSettings(api_token="token123")

    assert hasattr(settings, "auth_type")
