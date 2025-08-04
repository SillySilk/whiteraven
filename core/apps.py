from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    
    def ready(self):
        """
        Perform app initialization
        """
        # Import signal handlers and other initialization code
        from . import signals  # noqa
