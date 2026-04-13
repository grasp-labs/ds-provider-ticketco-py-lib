# ds-provider-ticketco-py-lib

A DS provider library for the [TicketCo](https://ticketco.events) event ticketing platform.

Wraps the TicketCo public REST API as a reusable, installable Python library,
exposing a **linked service** (authenticated HTTP connection) and a **dataset**
(paginated resource reads) via the standard DS provider interface.

## Resources

| Resource | API Endpoint | Description |
|---|---|---|
| `events` | `GET /api/public/v1/events` | Event listings |
| `customers` | `GET /api/public/v1/customers` | Customer records |
| `item_grosses` | `GET /api/public/v1/item_grosses` | Ticket/item gross sales |

## Installation

```bash
pip install ds-provider-ticketco-py-lib
```

## Quick start

```python
import os
from uuid import uuid4
from ds_provider_ticketco_py_lib.linked_service import (
    TicketcoLinkedService,
    TicketcoLinkedServiceSettings,
)
from ds_provider_ticketco_py_lib.dataset import (
    TicketcoDataset,
    TicketcoDatasetSettings,
    ReadSettings,
)
from ds_provider_ticketco_py_lib.enums import TicketcoResource

linked_service = TicketcoLinkedService(
    id=uuid4(),
    name="ticketco",
    version="1.0.0",
    settings=TicketcoLinkedServiceSettings(
        api_token=os.environ["TICKETCO_API_TOKEN"],
        host="https://demo.ticketco.events",   # omit for production
    ),
)
linked_service.connect()

dataset = TicketcoDataset(
    id=uuid4(),
    name="events",
    version="1.0.0",
    settings=TicketcoDatasetSettings(
        resource=TicketcoResource.EVENTS,
        read=ReadSettings(max_pages=5, columns=["id", "title", "start_at"]),
    ),
    linked_service=linked_service,
)
dataset.read()
df = dataset.output
print(df.head())
```

## Authentication

TicketCo uses a simple API token passed as the `token` query parameter on every request. 

## Links

- [API documentation](https://apidoc.ticketco.events/)
- [Demo environment](https://demo.ticketco.events)
