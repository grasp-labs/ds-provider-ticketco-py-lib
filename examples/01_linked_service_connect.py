"""
**File:** ``01_linked_service_connect.py``
**Region:** ``examples/01_linked_service_connect``

Example 01: Connect to TicketCo using a linked service.

This example demonstrates how to:
- Create a TicketCo linked service with an API token
- Test the connection to the TicketCo API
- Use the linked service as a foundation for dataset reads

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
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
)

from ds_provider_ticketco_py_lib.linked_service.ticketco import (
    TicketcoLinkedService,
    TicketcoLinkedServiceSettings,
)

Logger.configure(level=logging.DEBUG)
logger = Logger.get_logger(__name__)


def main() -> None:
    """Main function demonstrating TicketCo linked service connection."""
    api_token = os.getenv("TICKETCO_API_TOKEN")
    if not api_token:
        raise ValueError(
            "TICKETCO_API_TOKEN environment variable is required. "
            "See the Prerequisites section in this file's docstring for setup instructions."
        )
    host = os.getenv("TICKETCO_HOST", "https://demo.ticketco.events")

    settings = TicketcoLinkedServiceSettings(
        api_token=api_token,
        host=host,
    )

    linked_service = TicketcoLinkedService(
        id=uuid4(),
        name="TicketCo Linked Service",
        version="1.0.0",
        settings=settings,
    )

    try:
        linked_service.connect()
        logger.info("Testing connection to TicketCo (%s)...", host)
        success, message = linked_service.test_connection()

        if success:
            logger.info("Connection test successful!")
            logger.debug("Message: %s", message)
        else:
            logger.error("Connection test failed: %s", message)
            return

    except (ConnectionError, AuthenticationError, AuthorizationError) as exc:
        logger.error("Failed to connect to TicketCo: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise
    finally:
        linked_service.close()


if __name__ == "__main__":
    main()
