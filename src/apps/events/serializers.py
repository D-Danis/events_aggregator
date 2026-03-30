from rest_framework import serializers

from .models import Event, Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ["id", "name", "city", "address", "seats_pattern"]


class EventSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "place",
            "event_time",
            "registration_deadline",
            "status",
            "number_of_visitors",
            "changed_at",
            "created_at",
            "status_changed_at",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    seat = serializers.CharField(max_length=10)


class UnregisterSerializer(serializers.Serializer):
    ticket_id = serializers.UUIDField()
