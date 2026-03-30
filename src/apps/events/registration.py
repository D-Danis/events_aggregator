import logging
from django.utils import timezone
from django.db import transaction
from .models import Event, Registration
from .services.events_provider_client import EventsProviderClient
from django.conf import settings

logger = logging.getLogger(__name__)

class RegistrationError(Exception):
    pass

def get_event_or_404(event_id):
    try:
        return Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return None

def register_for_event(event_id, first_name, last_name, email, seat):
    event = get_event_or_404(event_id)
    if not event:
        raise RegistrationError("Event not found")
    if event.status != 'published':
        raise RegistrationError("Event is not published")
    if event.registration_deadline < timezone.now():
        raise RegistrationError("Registration deadline has passed")

    client = EventsProviderClient(
        base_url=settings.EVENTS_PROVIDER_URL,
        api_key=settings.EVENTS_PROVIDER_API_KEY,
    )
    try:
        seats_data = client.seats(event_id)
        available_seats = seats_data.get('seats', [])
    except Exception as e:
        logger.error("Failed to get seats from provider: %s", e)
        raise RegistrationError("Unable to check seat availability")
    if seat not in available_seats:
        raise RegistrationError(f"Seat {seat} is not available")

    try:
        response = client.register(event_id, first_name, last_name, email, seat)
        ticket_id = response.get('ticket_id')
        if not ticket_id:
            raise RegistrationError("No ticket_id returned")
    except Exception as e:
        logger.error("Provider registration failed: %s", e)
        raise RegistrationError("Registration with provider failed")

    with transaction.atomic():
        Registration.objects.create(
            ticket_id=ticket_id,
            event=event,
            seat=seat,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
    return ticket_id

def unregister_event(event_id, ticket_id):
    try:
        registration = Registration.objects.get(ticket_id=ticket_id, event_id=event_id)
    except Registration.DoesNotExist:
        raise RegistrationError("Registration not found")

    client = EventsProviderClient(
        base_url=settings.EVENTS_PROVIDER_URL,
        api_key=settings.EVENTS_PROVIDER_API_KEY,
    )
    try:
        client.unregister(event_id, ticket_id)
    except Exception as e:
        logger.error("Provider unregister failed: %s", e)
        raise RegistrationError("Unregistration with provider failed")

    registration.delete()
    return True