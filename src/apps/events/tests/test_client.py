import pytest
from unittest.mock import patch, MagicMock

from src.apps.events.services.events_provider_client import EventsProviderClient


@pytest.fixture
def client():
    """Создаёт клиент с отключёнными прокси для тестов."""
    base_url = "http://example.com"
    api_key = "test-api-key"
    return EventsProviderClient(base_url, api_key)


class TestEventsProviderClient:
    @patch("httpx.Client.request")
    def test_events(self, mock_request, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [], "next": None}
        mock_request.return_value = mock_response

        result = client.events("2026-03-01")

        mock_request.assert_called_once_with(
            "GET",
            "http://example.com/api/events/",
            headers={"x-api-key": "test-api-key"},
            params={"changed_at": "2026-03-01"},
        )
        assert result == {"results": [], "next": None}

    @patch("httpx.Client.request")
    def test_events_with_cursor(self, mock_request, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [], "next": "next_url"}
        mock_request.return_value = mock_response

        result = client.events("2026-03-01", cursor="abc123")

        mock_request.assert_called_once_with(
            "GET",
            "http://example.com/api/events/",
            headers={"x-api-key": "test-api-key"},
            params={"changed_at": "2026-03-01", "cursor": "abc123"},
        )
        assert result == {"results": [], "next": "next_url"}

    @patch("httpx.Client.request")
    def test_seats(self, mock_request, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"seats": ["A1", "A2"]}
        mock_request.return_value = mock_response

        result = client.seats("event-123")

        mock_request.assert_called_once_with(
            "GET",
            "http://example.com/api/events/event-123/seats/",
            headers={"x-api-key": "test-api-key"},
        )
        assert result == {"seats": ["A1", "A2"]}

    @patch("httpx.Client.request")
    def test_register(self, mock_request, client):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"ticket_id": "ticket-456"}
        mock_request.return_value = mock_response

        result = client.register(
            event_id="event-123",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            seat="A1",
        )

        expected_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "seat": "A1",
        }
        mock_request.assert_called_once_with(
            "POST",
            "http://example.com/api/events/event-123/register/",
            headers={"x-api-key": "test-api-key"},
            json=expected_data,
        )
        assert result == {"ticket_id": "ticket-456"}

    @patch("httpx.Client.request")
    def test_unregister(self, mock_request, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = client.unregister(event_id="event-123", ticket_id="ticket-456")

        mock_request.assert_called_once_with(
            "DELETE",
            "http://example.com/api/events/event-123/unregister/",
            headers={"x-api-key": "test-api-key"},
            json={"ticket_id": "ticket-456"},
        )
        assert result == {"success": True}
        