"""
**File:** ``test_dataset_settings.py``
**Region:** ``tests/dataset/unit_tests``

Unit tests for TicketcoDatasetSettings and ReadSettings.

Covers:
- ReadSettings defaults.
- TicketcoDatasetSettings stores resource correctly.
- dataset type property returns TICKETCO_DATASET.
- read() paginates and builds a DataFrame (mocked HTTP).
"""

from unittest.mock import MagicMock, PropertyMock, patch
from uuid import uuid4

import pandas as pd
import pytest
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

from ds_provider_ticketco_py_lib.dataset import (
    ReadSettings,
    TicketcoDataset,
    TicketcoDatasetSettings,
)
from ds_provider_ticketco_py_lib.enums import TicketcoResource
from ds_provider_ticketco_py_lib.linked_service import (
    TicketcoLinkedService,
    TicketcoLinkedServiceSettings,
)

# ---------------------------------------------------------------------------
# ReadSettings
# ---------------------------------------------------------------------------


def test_read_settings_defaults():
    """ReadSettings has None defaults for max_pages and columns."""
    settings = ReadSettings()
    assert settings.max_pages is None
    assert settings.columns is None


def test_read_settings_custom():
    """ReadSettings accepts max_pages and columns."""
    settings = ReadSettings(max_pages=3, columns=["id", "title"])
    assert settings.max_pages == 3
    assert settings.columns == ["id", "title"]


# ---------------------------------------------------------------------------
# TicketcoDatasetSettings
# ---------------------------------------------------------------------------


def test_dataset_settings_stores_resource():
    """TicketcoDatasetSettings stores the resource enum value."""
    settings = TicketcoDatasetSettings(resource=TicketcoResource.EVENTS)
    assert settings.resource == TicketcoResource.EVENTS


def test_dataset_settings_default_read():
    """TicketcoDatasetSettings has a default ReadSettings instance."""
    settings = TicketcoDatasetSettings(resource=TicketcoResource.CUSTOMERS)
    assert isinstance(settings.read, ReadSettings)


# ---------------------------------------------------------------------------
# TicketcoDataset type property
# ---------------------------------------------------------------------------


def _make_linked_service():
    return TicketcoLinkedService(
        settings=TicketcoLinkedServiceSettings(
            api_token="test_token",
            host="https://demo.ticketco.events",
        ),
        id=uuid4(),
        name="ls",
        version="1.0.0",
    )


def _make_dataset(resource=TicketcoResource.EVENTS, read=None):
    return TicketcoDataset(
        settings=TicketcoDatasetSettings(
            resource=resource,
            read=read or ReadSettings(),
        ),
        linked_service=_make_linked_service(),
        id=uuid4(),
        name="ds",
        version="1.0.0",
    )


def test_dataset_type_property():
    """type property returns TICKETCO_DATASET."""
    dataset = _make_dataset()
    assert dataset.type.name == "TICKETCO_DATASET"
    assert dataset.type == "DS.RESOURCE.DATASET.TICKETCO"


# ---------------------------------------------------------------------------
# read() — mocked HTTP
# ---------------------------------------------------------------------------


def _mock_response(data: list[dict], resource: str) -> MagicMock:
    response = MagicMock()
    response.json.return_value = {resource: data}
    return response


def test_read_fetches_all_pages():
    """read() paginates until an empty page and sets self.output."""
    dataset = _make_dataset(resource=TicketcoResource.EVENTS)

    page1 = [{"id": 1, "title": "Event A"}]
    page2 = [{"id": 2, "title": "Event B"}]
    page3: list[dict] = []

    connection_mock = MagicMock()
    connection_mock.get.side_effect = [
        _mock_response(page1, "events"),
        _mock_response(page2, "events"),
        _mock_response(page3, "events"),
    ]

    # Mock the read-only connection property using PropertyMock
    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ):
        dataset.read()

    assert isinstance(dataset.output, pd.DataFrame)
    assert len(dataset.output) == 2
    assert list(dataset.output["id"]) == [1, 2]


def test_read_respects_max_pages():
    """read() stops after max_pages even if more data is available."""
    dataset = _make_dataset(
        resource=TicketcoResource.CUSTOMERS,
        read=ReadSettings(max_pages=1),
    )

    page1 = [{"customer_id": 1, "email": "a@b.com"}]

    connection_mock = MagicMock()
    connection_mock.get.return_value = _mock_response(page1, "customers")

    # Mock the read-only connection property using PropertyMock
    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ):
        dataset.read()

    # Should only call get once (max_pages=1)
    assert connection_mock.get.call_count == 1
    assert len(dataset.output) == 1


def test_read_applies_column_filter():
    """read() filters to the requested columns."""
    dataset = _make_dataset(
        resource=TicketcoResource.EVENTS,
        read=ReadSettings(max_pages=1, columns=["id"]),
    )

    page1 = [{"id": 1, "title": "Event A", "start_at": "2024-01-01"}]

    connection_mock = MagicMock()
    connection_mock.get.side_effect = [
        _mock_response(page1, "events"),
        _mock_response([], "events"),
    ]

    # Mock the read-only connection property using PropertyMock
    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ):
        dataset.read()

    assert list(dataset.output.columns) == ["id"]


def test_read_empty_response_returns_empty_dataframe():
    """read() with no records returns an empty DataFrame."""
    dataset = _make_dataset(resource=TicketcoResource.ITEM_GROSSES)

    connection_mock = MagicMock()
    connection_mock.get.return_value = _mock_response([], "item_grosses")

    # Mock the read-only connection property using PropertyMock
    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ):
        dataset.read()

    assert isinstance(dataset.output, pd.DataFrame)
    assert dataset.output.empty


# ---------------------------------------------------------------------------
# Unsupported operations
# ---------------------------------------------------------------------------


def test_create_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.create()


def test_update_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.update()


def test_delete_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.delete()


def test_upsert_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.upsert()


def test_list_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.list()


def test_rename_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.rename()


def test_purge_raises_not_supported():
    dataset = _make_dataset()
    with pytest.raises(NotSupportedError):
        dataset.purge()


def test_close_calls_linked_service_close():
    """close() delegates to linked_service.close()."""
    dataset = _make_dataset()

    with patch.object(dataset.linked_service, "close") as mock_close:
        dataset.close()

    mock_close.assert_called_once()


# ---------------------------------------------------------------------------
# read() error handling
# ---------------------------------------------------------------------------


def test_read_propagates_authentication_error():
    """read() propagates AuthenticationError from connection."""
    dataset = _make_dataset(resource=TicketcoResource.EVENTS)

    connection_mock = MagicMock()
    connection_mock.get.side_effect = AuthenticationError(
        message="Invalid token",
        details={},
    )

    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ), pytest.raises(AuthenticationError):
        dataset.read()


def test_read_propagates_authorization_error():
    """read() propagates AuthorizationError from connection."""
    dataset = _make_dataset(resource=TicketcoResource.CUSTOMERS)

    connection_mock = MagicMock()
    connection_mock.get.side_effect = AuthorizationError(
        message="Forbidden",
        details={},
    )

    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ), pytest.raises(AuthorizationError):
        dataset.read()


def test_read_propagates_connection_error():
    """read() propagates ConnectionError from connection."""
    dataset = _make_dataset(resource=TicketcoResource.ITEM_GROSSES)

    connection_mock = MagicMock()
    connection_mock.get.side_effect = ConnectionError(
        message="Connection failed",
        details={},
    )

    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ), pytest.raises(ConnectionError):
        dataset.read()


def test_read_converts_resource_exception_to_read_error():
    """read() converts ResourceException to ReadError with dataset type in details."""
    dataset = _make_dataset(resource=TicketcoResource.EVENTS)

    connection_mock = MagicMock()
    connection_mock.get.side_effect = ResourceException(
        message="API error",
        status_code=500,
        details={"original": "error"},
    )

    with patch.object(
        type(dataset.linked_service),
        "connection",
        new_callable=PropertyMock,
        return_value=connection_mock
    ), pytest.raises(ReadError) as exc_info:
        dataset.read()

    # Verify ReadError has the right message and details
    assert "API error" in str(exc_info.value)
    assert exc_info.value.details["type"] == "DS.RESOURCE.DATASET.TICKETCO"
    assert exc_info.value.details["resource"] == "events"
    assert exc_info.value.details["original"] == "error"
