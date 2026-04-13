"""
**File:** ``__init__.py``
**Region:** ``ds_provider_ticketco_py_lib/linked_service``

TicketCo Linked Service

This module implements a linked service for TicketCo and provides a session.

Example:
    >>> from uuid import UUID
    >>> linked_service = TicketcoLinkedService(
    ...     id=UUID("00000000-0000-0000-0000-000000000000"),
    ...     name="test-name",
    ...     version="1.0.0",
    ...     settings=TicketcoLinkedServiceSettings(
    ...         api_token="your_api_token",
    ...     ),
    ... )
    >>> linked_service.connect()
    >>> linked_service.test_connection()
"""

from .ticketco import TicketcoLinkedService, TicketcoLinkedServiceSettings

__all__ = [
    "TicketcoLinkedService",
    "TicketcoLinkedServiceSettings",
]
