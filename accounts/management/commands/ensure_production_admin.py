import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or repair the production admin account."

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        first_name = os.environ.get("ADMIN_FIRST_NAME", "").strip()
        last_name = os.environ.get("ADMIN_LAST_NAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not all([email, username, first_name, last_name, password]):
            raise CommandError(
                "Set all ADMIN_EMAIL, ADMIN_USERNAME, "
                "ADMIN_FIRST_NAME, ADMIN_LAST_NAME and ADMIN_PASSWORD "
                "environment variables."
            )

        user = User.objects.filter(email__iexact=email).first()

        username_owner = User.objects.filter(username=username).first()
        if username_owner and username_owner.pk != getattr(user, "pk", None):
            raise CommandError(
                "That username already belongs to another account. "
                "Choose a different ADMIN_USERNAME."
            )

        if user is None:
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_no="",
            )
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.is_superadmin = True
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS("Production admin account configured.")
        )