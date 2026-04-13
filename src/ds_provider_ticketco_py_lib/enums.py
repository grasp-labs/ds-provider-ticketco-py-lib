"""
**File:** ``enums.py``
**Region:** ``ds_provider_ticketco_py_lib/enums``

Constants for TicketCo provider.

Example:
    >>> ResourceType.TICKETCO_LINKED_SERVICE
    'DS.RESOURCE.LINKED_SERVICE.TICKETCO'
    >>> ResourceType.TICKETCO_DATASET
    'DS.RESOURCE.DATASET.TICKETCO'
    >>> TicketcoResource.EVENTS
    'events'
"""

from enum import StrEnum


class ResourceType(StrEnum):
    """
    Constants for TicketCo provider.
    """

    TICKETCO_LINKED_SERVICE = "DS.RESOURCE.LINKED_SERVICE.TICKETCO"
    TICKETCO_DATASET = "DS.RESOURCE.DATASET.TICKETCO"


class TicketcoResource(StrEnum):
    """
    Available API resources in the TicketCo public v1 API.
    """

    EVENTS = "events"
    CUSTOMERS = "customers"
    ITEM_GROSSES = "item_grosses"
