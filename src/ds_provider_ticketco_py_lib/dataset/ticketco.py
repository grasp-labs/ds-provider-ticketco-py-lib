"""
**File:** ``ticketco.py``
**Region:** ``ds_provider_ticketco_py_lib/dataset/ticketco``

TicketCo Dataset

This module implements a dataset for the TicketCo REST API. It supports reading
the ``events``, ``customers``, and ``item_grosses`` endpoints with automatic
page-based pagination.

Example:
    >>> from uuid import uuid4
    >>> linked_service = TicketcoLinkedService(
    ...     id=uuid4(),
    ...     name="ticketco-ls",
    ...     version="1.0.0",
    ...     settings=TicketcoLinkedServiceSettings(
    ...         api_token="your_api_token",
    ...         host="https://demo.ticketco.events",
    ...     ),
    ... )
    >>> linked_service.connect()
    >>> dataset = TicketcoDataset(
    ...     id=uuid4(),
    ...     name="ticketco-events",
    ...     version="1.0.0",
    ...     settings=TicketcoDatasetSettings(
    ...         resource=TicketcoResource.EVENTS,
    ...         read=ReadSettings(max_pages=5),
    ...     ),
    ...     linked_service=linked_service,
    ... )
    >>> dataset.read()
    >>> df = dataset.output
"""

from dataclasses import dataclass, field
from typing import Any, Generic, NoReturn, TypeVar

import pandas as pd
from ds_common_logger_py_lib import Logger
from ds_resource_plugin_py_lib.common.resource.dataset import (
    DatasetSettings,
    DatasetStorageFormatType,
    TabularDataset,
)
from ds_resource_plugin_py_lib.common.resource.dataset.errors import ReadError
from ds_resource_plugin_py_lib.common.resource.errors import (
    NotSupportedError,
    ResourceException,
)
from ds_resource_plugin_py_lib.common.resource.linked_service.errors import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
)
from ds_resource_plugin_py_lib.common.serde.deserialize import PandasDeserializer
from ds_resource_plugin_py_lib.common.serde.serialize import PandasSerializer

from ..enums import ResourceType, TicketcoResource
from ..linked_service.ticketco import TicketcoLinkedService

logger = Logger.get_logger(__name__, package=True)

_API_PATH = "/api/public/v1"


@dataclass(kw_only=True)
class ReadSettings:
    """
    Read-specific settings for a TicketCo dataset.

    Attributes:
        max_pages: Maximum number of pages to fetch. ``None`` fetches all pages.
        columns: Column subset to return. ``None`` returns all columns.
    """

    max_pages: int | None = None
    """Cap the number of pages fetched. None = fetch all available pages."""

    columns: list[str] | None = None
    """Return only the specified columns. None = return all columns."""


@dataclass(kw_only=True)
class TicketcoDatasetSettings(DatasetSettings):
    """
    Settings for a TicketCo dataset.

    Attributes:
        resource: The TicketCo API resource to read.
        read: Read-specific options (pagination, column selection).
    """

    resource: TicketcoResource
    """The API resource to read (events, customers, or item_grosses)."""

    read: ReadSettings = field(default_factory=ReadSettings)
    """Read-specific options."""


TicketcoDatasetSettingsType = TypeVar(
    "TicketcoDatasetSettingsType",
    bound=TicketcoDatasetSettings,
)
TicketcoLinkedServiceType = TypeVar(
    "TicketcoLinkedServiceType",
    bound=TicketcoLinkedService[Any],
)


@dataclass(kw_only=True)
class TicketcoDataset(
    TabularDataset[
        TicketcoLinkedServiceType,
        TicketcoDatasetSettingsType,
        PandasSerializer,
        PandasDeserializer,
    ],
    Generic[TicketcoLinkedServiceType, TicketcoDatasetSettingsType],
):
    """
    Dataset for reading data from the TicketCo REST API.

    Paginates through the selected resource endpoint and returns the result
    as a ``pandas.DataFrame``.
    """

    linked_service: TicketcoLinkedServiceType
    settings: TicketcoDatasetSettingsType

    serializer: PandasSerializer | None = field(
        default_factory=lambda: PandasSerializer(format=DatasetStorageFormatType.JSON),
    )
    deserializer: PandasDeserializer | None = field(
        default_factory=lambda: PandasDeserializer(format=DatasetStorageFormatType.JSON),
    )

    @property
    def type(self) -> ResourceType:
        return ResourceType.TICKETCO_DATASET

    def read(self) -> None:
        """
        Read all records from the configured TicketCo resource endpoint.

        Paginates starting from page 1 and stops when the API returns an empty
        list or ``max_pages`` is reached. Sets ``self.output`` to a
        ``pandas.DataFrame`` containing all collected records.

        Raises:
            AuthenticationError: If authentication fails.
            AuthorizationError: If the request is forbidden.
            ConnectionError: If the connection fails.
            ReadError: If the API returns an unexpected error.
        """
        resource = self.settings.resource
        api_token = self.linked_service.settings.api_token
        url = f"{self.linked_service.base_uri}{_API_PATH}/{resource}"

        logger.debug("Reading TicketCo resource '%s' from %s", resource, url)

        records: list[dict[str, Any]] = []
        page = 1

        try:
            while True:
                params = {"token": api_token, "page": page}
                response = self.linked_service.connection.get(url, params=params)
                page_records: list[dict[str, Any]] = response.json().get(resource, [])

                if not page_records:
                    logger.debug("Empty page at page=%d — stopping pagination", page)
                    break

                records.extend(page_records)
                logger.debug("Fetched %d records on page %d", len(page_records), page)

                if self.settings.read.max_pages and page >= self.settings.read.max_pages:
                    logger.debug("Reached max_pages=%d — stopping", self.settings.read.max_pages)
                    break

                page += 1

        except (AuthenticationError, AuthorizationError, ConnectionError) as exc:
            raise exc
        except ResourceException as exc:
            exc.details.update({"type": self.type.value, "resource": resource})
            raise ReadError(
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
            ) from exc

        df = pd.DataFrame(records)

        if self.settings.read.columns and not df.empty:
            existing = [c for c in self.settings.read.columns if c in df.columns]
            df = df[existing]

        self.output = df
        logger.debug("Read complete: %d total records", len(records))

    def create(self) -> NoReturn:
        raise NotSupportedError("Create is not supported for TicketCo datasets")

    def update(self) -> NoReturn:
        raise NotSupportedError("Update is not supported for TicketCo datasets")

    def delete(self) -> NoReturn:
        raise NotSupportedError("Delete is not supported for TicketCo datasets")

    def upsert(self) -> NoReturn:
        raise NotSupportedError("Upsert is not supported for TicketCo datasets")

    def list(self) -> NoReturn:
        raise NotSupportedError("List is not supported for TicketCo datasets")

    def rename(self) -> NoReturn:
        raise NotSupportedError("Rename is not supported for TicketCo datasets")

    def purge(self) -> NoReturn:
        raise NotSupportedError("Purge is not supported for TicketCo datasets")

    def close(self) -> None:
        self.linked_service.close()
