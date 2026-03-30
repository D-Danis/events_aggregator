from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения событий.
    Доступны методы: list (GET /api/events/) и retrieve (GET /api/events/{id}/).
    """

    queryset = Event.objects.select_related("place").all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
