from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from incidents.permissions import ADMIN_GROUP, ANALYST_GROUP


class Command(BaseCommand):
    help = "Create the Incident Desk analyst and administrator groups."

    def handle(self, *args, **options):
        for name in (ANALYST_GROUP, ADMIN_GROUP):
            _, created = Group.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Exists'}: {name}"))
