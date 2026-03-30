import uuid

from django.db import models


class Place(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    seats_pattern = models.CharField(max_length=500)
    changed_at = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class Event(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("published", "Published"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="events")
    event_time = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    number_of_visitors = models.PositiveIntegerField(default=0)
    changed_at = models.DateTimeField()
    created_at = models.DateTimeField()
    status_changed_at = models.DateTimeField()

    class Meta:
        ordering = ["-event_time"]

    def __str__(self):
        return self.name


class Registration(models.Model):
    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    seat = models.CharField(max_length=10)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "seat")
        ordering = ["registered_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.event.name} ({self.seat})"


class SyncState(models.Model):
    name = models.CharField(max_length=100, unique=True, default="last_sync")
    last_sync = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
