from decimal import Decimal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from wallet.models import DataPlan

from collections import Counter

NETWORKS = {"1": "mtn", "2": "airtel", "3": "9mobile", "4": "glo"}


class Command(BaseCommand):
    help = "Load DodoData plans. New plans start inactive; existing ones keep your price and active flag."

    def handle(self, *args, **options):
        try:
            r = requests.get(
                f"{settings.DODODATA_BASE_URL}/api/data/plans",
                headers={"Authorization": f"Token {settings.DODODATA_API_KEY}"},
                timeout=30,
            )
            plans = r.json()
        except requests.HTTPError as e:
            self.stdout.write(f"DodoData returned HTTP {e.response.status_code}")
            return
        except (requests.RequestException, ValueError):
            self.stdout.write("Request failed")
            return
        if not isinstance(plans, list):
            self.stdout.write(f"Unexpected reply: {str(plans)[:200]}")
            return

        added = 0
        for p in plans:
            network = NETWORKS.get(str(p.get("network")))
            price = Decimal(str(p.get("priceForNormalUser") or 0))
            if not network or price <= 0:
                continue
            _, created = DataPlan.objects.get_or_create(
                provider="dododata",
                network=network,
                variation_code=str(p["id"]),
                defaults={
                    "name": f'{p.get("title", "")} ({p.get("dataType", "")})',
                    "price": price,
                    "is_active": False,
                },
            )
            added += created
        self.stdout.write(f"{len(plans)} from DodoData, {added} new (inactive)")