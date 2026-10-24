from decimal import Decimal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from wallet.models import DataPlan

SERVICE_IDS = {
    "mtn": "mtn-data",
    "glo": "glo-data",
    "airtel": "airtel-data",
    "9mobile": "etisalat-data",
}


class Command(BaseCommand):
    help = "Load data plans from VTPass. Existing plans keep your price and active flag."

    def handle(self, *args, **options):
        for network, service_id in SERVICE_IDS.items():
            try:
                r = requests.get(
                    f"{settings.VTPASS_BASE_URL}/service-variations",
                    params={"serviceID": service_id},
                    headers={
                        "api-key": settings.VTPASS_API_KEY,
                        "public-key": settings.VTPASS_PUBLIC_KEY,
                    },
                    timeout=30,
                )
                content = r.json().get("content") or {}
            except requests.HTTPError as e:
                self.stdout.write(f"VtPass returned HTTP {e.response.status_code}")
                return
            except (requests.RequestException, ValueError):
                self.stdout.write(f"{network}: request failed, skipped")
                continue

            variations = content.get("variations") or content.get("varations") or []
            added = 0
            for v in variations:
                if str(v.get("fixedPrice", "")).lower() != "yes":
                    continue
                price = Decimal(str(v["variation_amount"]))
                if price <= 0:
                    continue
                _, created = DataPlan.objects.get_or_create(
                    network=network,
                    variation_code=v["variation_code"],
                    defaults={"name": v["name"], "price": price},
                )
                added += created
            self.stdout.write(f"{network}: {len(variations)} from VTPass, {added} new")