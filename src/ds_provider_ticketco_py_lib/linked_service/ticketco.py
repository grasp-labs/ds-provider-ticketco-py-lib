"""
**File:** ``ticketco.py``
**Region:** ``ds_provider_ticketco_py_lib/linked_service/ticketco``

TicketCo Linked Service

This module implements a linked service for TicketCo, allowing users to connect
to and interact with the TicketCo REST API using an API token.

Example:
    >>> from uuid import uuid4
    >>> linked_service = TicketcoLinkedService(
    ...     settings=TicketcoLinkedServiceSettings(
    ...         api_token="your_api_token",
    ...     ),
    ...     id=uuid4(),
    ...     name="ticketco-connection",
    ...     version="1.0.0",
    ... )
    >>> linked_service.connect()
    >>> success, message = linked_service.test_connection()
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from ds_protocol_http_py_lib import HttpLinkedService, HttpLinkedServiceSettings, enums

from ..enums import ResourceType

# -------------------------------
# settings class
# -------------------------------

_PROD_HOST = "https://ticketco.events"


@dataclass(kw_only=True)
class TicketcoLinkedServiceSettings(HttpLinkedServiceSettings):
    """
    Settings required to connect to the TicketCo REST API.

    TicketCo uses a simple API token passed as a query parameter
    (``?token=<api_token>``) on every request. No header-based auth is needed.

    Attributes:
        api_token: The TicketCo API token.
        host: Base URL of the TicketCo API (default: production).
        auth_type: Authentication type — always NO_AUTH for TicketCo
            (the token is injected by the dataset layer as a query param).
    """

    api_token: str = field(repr=False, metadata={"mask": True})
    """The TicketCo API token. Masked in logs."""

    host: str = _PROD_HOST
    """Base URL. Override with 'https://demo.ticketco.events' for the demo env."""

    auth_type: enums.AuthType = enums.AuthType.NO_AUTH
    """Authentication type — always NO_AUTH; token is a query param."""


TicketcoLinkedServiceSettingsType = TypeVar(
    "TicketcoLinkedServiceSettingsType",
    bound="TicketcoLinkedServiceSettings",
)

# -------------------------------
# LinkedService class
# -------------------------------


@dataclass(kw_only=True)
class TicketcoLinkedService(
    HttpLinkedService[TicketcoLinkedServiceSettingsType],
    Generic[TicketcoLinkedServiceSettingsType],
):
    """
    Linked service for connecting to the TicketCo REST API.

    Inherits connection management, retry logic, and session handling from
    ``HttpLinkedService``. The TicketCo API token is stored in settings and
    injected as a query parameter by ``TicketcoDataset`` at request time.
    """

    settings: TicketcoLinkedServiceSettingsType

    @property
    def type(self) -> ResourceType:  # type: ignore[override]
        """
        Get the type of the linked service.

        Returns:
            ResourceType
        """
        return ResourceType.TICKETCO_LINKED_SERVICE
