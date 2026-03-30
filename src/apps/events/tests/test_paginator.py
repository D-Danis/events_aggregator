from unittest.mock import MagicMock

import pytest

from src.apps.events.paginator import EventsPaginator
from src.apps.events.services.events_provider_client import EventsProviderClient


@pytest.fixture
def mock_client():
    return MagicMock(spec=EventsProviderClient)


class TestEventsPaginator:
    def test_iterates_over_single_page(self, mock_client):
        events_page = {
            "results": [{"id": 1, "name": "Event 1"}, {"id": 2, "name": "Event 2"}],
            "next": None,
        }
        mock_client.events.return_value = events_page

        paginator = EventsPaginator(mock_client, "2026-03-01")
        events = list(paginator)

        assert len(events) == 2
        assert events[0] == {"id": 1, "name": "Event 1"}
        assert events[1] == {"id": 2, "name": "Event 2"}
        mock_client.events.assert_called_once_with("2026-03-01")

    def test_iterates_over_multiple_pages(self, mock_client):
        page1 = {
            "results": [{"id": 1}],
            "next": "http://example.com/api/events/?changed_at=2026-03-01&cursor=abc",
        }
        page2 = {
            "results": [{"id": 2}],
            "next": None,
        }
        mock_client.events.side_effect = [page1, page2]

        paginator = EventsPaginator(mock_client, "2026-03-01")
        events = list(paginator)

        assert len(events) == 2
        assert events[0] == {"id": 1}
        assert events[1] == {"id": 2}
        assert mock_client.events.call_count == 2
        mock_client.events.assert_any_call("2026-03-01")
        mock_client.events.assert_any_call("2026-03-01", cursor="abc")

    def test_handles_empty_page(self, mock_client):
        page = {"results": [], "next": None}
        mock_client.events.return_value = page

        paginator = EventsPaginator(mock_client, "2026-03-01")
        events = list(paginator)

        assert events == []

    def test_stops_when_next_is_none(self, mock_client):
        page = {"results": [{"id": 1}], "next": None}
        mock_client.events.return_value = page

        paginator = EventsPaginator(mock_client, "2026-03-01")
        events = list(paginator)

        assert len(events) == 1
        assert events[0] == {"id": 1}
