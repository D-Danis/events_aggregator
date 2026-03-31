import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from src.apps.events.models import Event, Place, Registration
from src.apps.events.registration import (
    RegistrationError,
    register_for_event,
    unregister_event,
)


@pytest.fixture
def event():
    place = Place.objects.create(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Place",
        city="Test City",
        address="123 Test St",
        seats_pattern="A1-10",
        changed_at=timezone.now(),
        created_at=timezone.now(),
    )
    event = Event.objects.create(
        id="550e8400-e29b-41d4-a716-446655440001",
        name="Test Event",
        place=place,
        event_time=timezone.now() + timedelta(days=10),
        registration_deadline=timezone.now() + timedelta(days=5),
        status="published",
        number_of_visitors=0,
        changed_at=timezone.now(),
        created_at=timezone.now(),
        status_changed_at=timezone.now(),
    )
    return event


@pytest.mark.django_db
def test_register_for_event_success(event):
    ticket_uuid = uuid.uuid4()
    with patch(
        "src.apps.events.registration.EventsProviderClient"
    ) as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.seats.return_value = {"seats": ["A1", "A2"]}
        mock_client.register.return_value = {"ticket_id": str(ticket_uuid)}

        ticket_id = register_for_event(
            event.id, "John", "Doe", "john@example.com", "A1"
        )
        assert ticket_id == str(ticket_uuid)
        mock_client.seats.assert_called_once_with(event.id)
        mock_client.register.assert_called_once_with(
            event.id, "John", "Doe", "john@example.com", "A1"
        )
        assert Registration.objects.filter(ticket_id=ticket_uuid).exists()


@pytest.mark.django_db
def test_register_for_event_seat_not_available(event):
    with patch(
        "src.apps.events.registration.EventsProviderClient"
    ) as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.seats.return_value = {"seats": ["A2"]}
        with pytest.raises(RegistrationError, match="Seat A1 is not available"):
            register_for_event(event.id, "John", "Doe", "john@example.com", "A1")


@pytest.mark.django_db
def test_unregister_event_success(event):
    ticket_uuid = uuid.uuid4()

    with patch(
        "src.apps.events.registration.EventsProviderClient"
    ) as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.unregister.return_value = {"success": True}
        unregister_event(event.id, str(ticket_uuid))
        mock_client.unregister.assert_called_once_with(event.id, str(ticket_uuid))
        assert not Registration.objects.filter(ticket_id=ticket_uuid).exists()
