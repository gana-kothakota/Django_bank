from django.contrib import admin
from .models import ContentView
from typing import Any
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


class ContentViewInline(GenericTabularInline):
    model = ContentView
    extra = 0
    readonly_fields = [
        "user",
        "viewer_ip",
        "last_viewed",
        "created_at",
    ]
    can_delete = True

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    list_display = (
        "content_type",
        "object_id",
        "user",
        "viewer_ip",
        "last_viewed",
    )
    list_filter = (
        "content_type",
        "created_at",
        "last_viewed",
    )
    date_hierarchy = "last_viewed"
    readonly_fields = [
        "content_type",
        "object_id",
        "user",
        "viewer_ip",
        "last_viewed",
        "created_at",
        "updated_at",
    ]

    search_fields = (
        "content_type",
        "object_id",
        "user",
        "viewer_ip",
    )
    ordering = ("-last_viewed",)

    fieldsets = (
        (
            _("Content"),
            {
                "fields": (
                    "content_type",
                    "object_id",
                    "content_object",
                )
            },
        ),
        (
            _("View Data"),
            {
                "fields": (
                    "user",
                    "viewer_ip",
                    "last_viewed",
                )
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: ContentView = None
    ) -> bool:
        return False
