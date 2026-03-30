from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .registration import RegistrationError, register_for_event, unregister_event
from .serializers import EventSerializer, RegisterSerializer, UnregisterSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения событий.
    Доступны методы: list (GET /api/events/) и retrieve (GET /api/events/{id}/).
    """

    queryset = Event.objects.select_related("place").all()
    serializer_class = EventSerializer

    @action(detail=True, methods=["post"], url_path="register")
    def register(self, request, pk=None):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ticket_id = register_for_event(
                event_id=pk,
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                email=serializer.validated_data["email"],
                seat=serializer.validated_data["seat"],
            )
            return Response({"ticket_id": ticket_id}, status=status.HTTP_201_CREATED)
        except RegistrationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="unregister")
    def unregister(self, request, pk=None):
        serializer = UnregisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            unregister_event(
                event_id=pk, ticket_id=serializer.validated_data["ticket_id"]
            )
            return Response({"success": True}, status=status.HTTP_200_OK)
        except RegistrationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
