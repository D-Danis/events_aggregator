import logging
from celery import shared_task
from django.utils import timezone

from src.apps.events.models import Event, Place, SyncState
from src.apps.events.services.events_provider_client import EventsProviderClient
from src.apps.events.paginator import EventsPaginator
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def sync_events_task():
    """Периодическая синхронизация событий из Events Provider API."""
    logger.info("Starting events synchronization")

    # Получаем дату последней синхронизации
    sync_state, _ = SyncState.objects.get_or_create(name='last_sync')
    last_sync = sync_state.last_sync
    changed_at = last_sync.strftime('%Y-%m-%d') if last_sync else '2026-01-01'

    # Создаём клиент
    client = EventsProviderClient(
        base_url=settings.EVENTS_PROVIDER_URL,
        api_key=settings.EVENTS_PROVIDER_API_KEY,
    )
    paginator = EventsPaginator(client, changed_at)

    saved_count = 0
    for event_data in paginator:
        # Сохраняем или обновляем площадку
        place_data = event_data.pop('place')
        place, _ = Place.objects.update_or_create(
            id=place_data['id'],
            defaults={
                'name': place_data['name'],
                'city': place_data['city'],
                'address': place_data['address'],
                'seats_pattern': place_data['seats_pattern'],
                'changed_at': place_data['changed_at'],
                'created_at': place_data['created_at'],
            }
        )

        # Сохраняем или обновляем событие
        Event.objects.update_or_create(
            id=event_data['id'],
            defaults={
                'name': event_data['name'],
                'place': place,
                'event_time': event_data['event_time'],
                'registration_deadline': event_data['registration_deadline'],
                'status': event_data['status'],
                'number_of_visitors': event_data.get('number_of_visitors', 0),
                'changed_at': event_data['changed_at'],
                'created_at': event_data['created_at'],
                'status_changed_at': event_data['status_changed_at'],
            }
        )
        saved_count += 1

    # Обновляем дату последней синхронизации
    sync_state.last_sync = timezone.now()
    sync_state.save()

    logger.info(f"Events synchronization finished. Saved/updated {saved_count} events.")