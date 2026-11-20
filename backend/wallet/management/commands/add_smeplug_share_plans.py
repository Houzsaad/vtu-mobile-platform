from decimal import Decimal

from django.core.management.base import BaseCommand

from wallet.models import DataPlan

# Your cost per GB from the vendor's figure (3,500 for 11GB). Change it in the admin if it differs.
COST_PER_GB = Decimal("318")

# (SMEPlug code, size label, size in GB, example selling price)
PLANS = [
    ("517", "500MB", Decimal("0.5"), Decimal("250")),
    ("518", "1GB", Decimal("1"), Decimal("390")),
    ("519", "2GB", Decimal("2"), Decimal("750")),
    ("520", "3GB", Decimal("3"), Decimal("1200")),
]


class Command(BaseCommand):
    help = "Add MTN Data Share plans from the SMEPlug dashboard. Inactive, and existing rows are left alone."

    def handle(self, *args, **options):
        created = 0
        for code, label, gb, price in PLANS:
            _, was_created = DataPlan.objects.get_or_create(
                provider="smeplug",
                network="mtn",
                variation_code=code,
                defaults={
                    "name": f"{label} (Share)",
                    "plan_type": "Share",
                    "cost_price": (COST_PER_GB * gb).quantize(Decimal("0.01")),
                    "price": price,
                    "is_active": False,
                },
            )
            created += was_created
        self.stdout.write(f"{created} added (inactive), {len(PLANS) - created} already there")