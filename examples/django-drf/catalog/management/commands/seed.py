from django.core.management.base import BaseCommand

from catalog.models import Product
from catalog.views import DEMO_PRODUCTS


class Command(BaseCommand):
    help = "Insert demo products if the catalog is empty."

    def handle(self, *args: object, **options: object) -> None:
        created = 0
        for item in DEMO_PRODUCTS:
            _, was_created = Product.objects.get_or_create(sku=item["sku"], defaults=item)
            if was_created:
                created += 1
        self.stdout.write(f"Seeded {created} products ({Product.objects.count()} total).")
