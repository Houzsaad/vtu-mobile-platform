import re
from decimal import Decimal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from wallet.models import DataPlan

NETWORKS = {"1": "mtn", "2": "airtel", "3": "9mobile", "4": "glo"}

def split_name(raw):
    """'1GB [SME]' -> ('1GB', 'SME'). Plans without brackets get type 'Data'."""
    raw = (raw or "").strip()
    match = re.search(r"\[([^\]]+)\]", raw)
    plan_type = match.group(1).strip() if match else "Data"
    base = re.sub(r"\s*\[[^\]]+\]\s*", " ", raw).strip()
    return base, plan_type


class Command(BaseCommand):
    help = "Load SMEPlug plans. New plans start inactive; existing ones keep your price and active flag."

    def handle(self, *args, **options):
        try:
            r = requests.get(
                f"{settings.SMEPLUG_BASE_URL}/data/plans",
                headers={"Authorization": f"Bearer {settings.SMEPLUG_SECRET_KEY}"},
                timeout=30,
            )
            body = r.json()
        except (requests.RequestException, ValueError):
            self.stdout.write("Request failed")
            return
        if not body.get("status") or not isinstance(body.get("data"), dict):
            self.stdout.write(f"Unexpected reply: {str(body)[:200]}")
            return

        existing = {
            (p.network, p.variation_code): p
            for p in DataPlan.objects.filter(provider="smeplug")
        }
        to_create, to_update = [], []

        for network_id, plans in body["data"].items():
            network = NETWORKS.get(str(network_id))
            if not network:
                continue
            for p in plans:
                price = Decimal(str(p.get("price") or 0))
                if price <= 0:
                    continue
                code = str(p["id"])
                base, plan_type = split_name(p.get("name"))
                obj = existing.get((network, code))
                if obj:
                    obj.plan_type = plan_type
                    obj.cost_price = price
                    to_update.append(obj)
                else:
                    to_create.append(DataPlan(
                        provider="smeplug",
                        network=network,
                        variation_code=code,
                        name=f"{base} ({plan_type})",
                        price=price,
                        cost_price=price,
                        plan_type=plan_type,
                        is_active=False,
                    ))

        DataPlan.objects.bulk_create(to_create)
        DataPlan.objects.bulk_update(to_update, ["plan_type", "cost_price"])
        self.stdout.write(f"{len(to_create)} new (inactive), {len(to_update)} updated")