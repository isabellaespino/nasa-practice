from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apod.models import ApodEntry

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "apod-demo-pass"

SEED_ENTRIES = [
    {
        "date": date(1995, 6, 16),
        "title": "Comet Hyakutake's Ion Tail",
        "explanation": (
            "This is the first entry ever published by NASA's Astronomy "
            "Picture of the Day, featuring the ion tail of Comet Hyakutake."
        ),
        "media_type": ApodEntry.IMAGE,
        "url": "https://apod.nasa.gov/apod/image/9506/hyakutake_kmt_big.jpg",
    },
    {
        "date": date(2015, 6, 16),
        "title": "20 Years of APOD",
        "explanation": "A retrospective entry marking two decades of the Astronomy Picture of the Day.",
        "media_type": ApodEntry.IMAGE,
        "url": "https://apod.nasa.gov/apod/image/1506/heic1512a.jpg",
    },
]


class Command(BaseCommand):
    help = "Seed a demo user account and a few cached APOD entries for a fresh clone."

    def handle(self, *args, **options):
        User = get_user_model()
        _, created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={"is_staff": False, "is_superuser": False},
        )
        if created:
            user = User.objects.get(username=DEMO_USERNAME)
            user.set_password(DEMO_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user '{DEMO_USERNAME}'."))
        else:
            self.stdout.write(f"Demo user '{DEMO_USERNAME}' already exists, skipping.")

        for data in SEED_ENTRIES:
            _, created = ApodEntry.objects.get_or_create(date=data["date"], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Seeded APOD entry for {data['date']}."))
            else:
                self.stdout.write(f"APOD entry for {data['date']} already exists, skipping.")
