import uuid
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.apps.events.models import Event, Place


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def event():
    place = Place.objects.create(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Place",
        city="Test City",
        address="123 Test St",
        seats_pattern="A1-10",
        changed_at="2026-01-01T00:00:00Z",
        created_at="2026-01-01T00:00:00Z",
    )
    event = Event.objects.create(
        id="550e8400-e29b-41d4-a716-446655440001",
        name="Test Event",
        place=place,
        event_time="2026-02-01T00:00:00Z",
        registration_deadline="2026-01-15T00:00:00Z",
        status="published",
        number_of_visitors=0,
        changed_at="2026-01-01T00:00:00Z",
        created_at="2026-01-01T00:00:00Z",
        status_changed_at="2026-01-01T00:00:00Z",
    )
    return event


@pytest.mark.django_db
@patch("src.apps.events.views.register_for_event")
def test_register_endpoint_success(mock_register, api_client, event):
    ticket_uuid = uuid.uuid4()
    mock_register.return_value = str(ticket_uuid)
    url = reverse("event-register", args=[event.id])
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "seat": "A1",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["ticket_id"] == str(ticket_uuid)


@pytest.mark.django_db
@patch("src.apps.events.views.unregister_event")
def test_unregister_endpoint_success(mock_unregister, api_client, event):
    mock_unregister.return_value = True
    url = reverse("event-unregister", args=[event.id])
    ticket_uuid = uuid.uuid4()
    data = {"ticket_id": str(ticket_uuid)}
    response = api_client.delete(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
