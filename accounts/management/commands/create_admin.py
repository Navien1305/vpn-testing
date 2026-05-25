import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import UserRole


class Command(BaseCommand):
    help = "Creates or updates an approved administrator without interactive prompts."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin"))
        parser.add_argument("--password", default=os.getenv("DJANGO_SUPERUSER_PASSWORD"))
        parser.add_argument("--full-name", default=os.getenv("DJANGO_SUPERUSER_FULL_NAME"))

    def handle(self, *args, **options):
        username = options["username"].strip()
        password = options["password"]
        full_name = (options["full_name"] or username).strip()

        if not username:
            raise CommandError("Username is required.")
        if not password:
            raise CommandError("Password is required. Pass --password or set DJANGO_SUPERUSER_PASSWORD.")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "full_name": full_name,
                "role": UserRole.ADMIN,
                "is_approved": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.full_name = full_name
        user.role = UserRole.ADMIN
        user.is_approved = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Administrator {username!r} {action}."))
