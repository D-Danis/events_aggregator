from django.contrib import admin

from .models import Event, Place, Registration


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "created_at", "changed_at")
    search_fields = ("name", "city")
    readonly_fields = ("id", "created_at", "changed_at")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "place", "event_time", "status", "number_of_visitors")
    list_filter = ("status", "place")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "changed_at", "status_changed_at")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "event",
        "seat",
        "first_name",
        "last_name",
        "registered_at",
    )
    list_filter = ("event",)
    search_fields = ("first_name", "last_name", "email")
    readonly_fields = ("ticket_id", "registered_at")
