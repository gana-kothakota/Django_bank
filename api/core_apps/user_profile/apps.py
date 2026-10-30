from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from loguru import logger

class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.user_profile"
    verbose_name = _("user_profile")

    def ready(self) -> None:
        """Connect the signals when the app is ready."""
        try:
            import core_apps.user_profile.signals
        except ImportError as e:
            logger.error(f"Failed to import signals: {e}")
