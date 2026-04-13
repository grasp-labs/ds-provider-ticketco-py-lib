"""
**File:** ``02_dataset_read.py``
**Region:** ``examples/02_dataset_read``

Example 02: Read data from TicketCo using a dataset.

This example demonstrates how to:
- Create a TicketCo linked service
- Read the ``events`` resource into a pandas DataFrame
- Apply column filtering and page limits

Prerequisites:
    Set environment variables:
    - TICKETCO_API_TOKEN: Your TicketCo API token (required)
    - TICKETCO_HOST: (optional) Override host, e.g. https://demo.ticketco.events

    For demo/testing, you can use the public demo token:
        export TICKETCO_API_TOKEN="my_token"
        export TICKETCO_HOST="https://demo.ticketco.events"
"""

from __future__ import annotations

import logging
import os
from uuid import uuid4

from ds_common_logger_py_lib import Logger
from ds_resource_plugin_py_lib.common.resource.dataset.errors import ReadError
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
)

from ds_provider_ticketco_py_lib.dataset.ticketco import (
    ReadSettings,
    TicketcoDataset,
    TicketcoDatasetSettings,
)
from ds_provider_ticketco_py_lib.enums import TicketcoResource
from ds_provider_ticketco_py_lib.linked_service.ticketco import (
    TicketcoLinkedService,
    TicketcoLinkedServiceSettings,
)

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def main() -> None:
    """Main function demonstrating TicketCo dataset read."""
    api_token = os.getenv("TICKETCO_API_TOKEN")
    if not api_token:
        raise ValueError(
            "TICKETCO_API_TOKEN environment variable is required. "
            "See the Prerequisites section in this file's docstring for setup instructions."
        )
    host = os.getenv("TICKETCO_HOST", "https://demo.ticketco.events")

    linked_service = TicketcoLinkedService(
        id=uuid4(),
        name="TicketCo Linked Service",
        version="1.0.0",
        settings=TicketcoLinkedServiceSettings(
            api_token=api_token,
            host=host,
        ),
    )
    linked_service.connect()

    dataset = TicketcoDataset(
        id=uuid4(),
        name="TicketCo Events Dataset",
        version="1.0.0",
        settings=TicketcoDatasetSettings(
            resource=TicketcoResource.EVENTS,
            read=ReadSettings(
                max_pages=2,
                columns=["id", "title", "start_at", "end_at"],
            ),
        ),
        linked_service=linked_service,
    )

    try:
        logger.info("Reading events from TicketCo...")
        dataset.read()
        df = dataset.output
        logger.info("Fetched %d events", len(df))
        print(df.head())
    except (ConnectionError, AuthenticationError, AuthorizationError) as exc:
        logger.error("Failed to connect to TicketCo: %s", exc)
        raise
    except ReadError as exc:
        logger.error("Failed to read data from TicketCo: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise
    finally:
        linked_service.close()


if __name__ == "__main__":
    main()
