from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def create_admin_groups(sender, **kwargs):
    """
    Create admin groups and set permissions after migrations
    """
    if sender.name == 'core':
        from django.core.management import call_command
        try:
            call_command('setup_admin_groups')
        except Exception as e:
            print(f"Warning: Could not set up admin groups: {e}")