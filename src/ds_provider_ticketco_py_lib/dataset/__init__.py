"""
**File:** ``__init__.py``
**Region:** ``ds_provider_ticketco_py_lib/dataset``

TicketCo Dataset

This module implements a dataset for the TicketCo REST API.

Example:
    >>> dataset = TicketcoDataset(
    ...     settings=TicketcoDatasetSettings(
    ...         resource=TicketcoResource.EVENTS,
    ...     ),
    ...     linked_service=linked_service,
    ... )
    >>> dataset.read()
    >>> df = dataset.output
"""

from .ticketco import ReadSettings, TicketcoDataset, TicketcoDatasetSettings

__all__ = [
    "ReadSettings",
    "TicketcoDataset",
    "TicketcoDatasetSettings",
]
