import re
from decimal import Decimal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from wallet.models import DataPlan

NETWORKS = {"1": "mtn", "2": "airtel", "3": "9mobile", "4": "glo"}


def split_name(raw):
    """'1GB [SME]' -> ('1GB', 'SME'). Names with 'Share' get type 'Share'. Otherwise 'Data'."""
    raw = (raw or "").strip()
    match = re.search(r"\[([^\]]+)\]", raw)
    base = re.sub(r"\s*\[[^\]]+\]\s*", " ", raw).strip()
    if match:
        return base, match.group(1).strip()
    if "share" in base.lower():
        return base, "Share"
    return base, "Data"


class Command(BaseCommand):
    help = (
        "Load SMEPlug plans. New plans start inactive. Existing plans keep their "
        "price, cost price, name and active flag; only the plan type is refreshed."
    )

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
        unpriced = 0

        for network_id, plans in body["data"].items():
            network = NETWORKS.get(str(network_id))
            if not network:
                continue
            for p in plans:
                code = str(p["id"])
                base, plan_type = split_name(p.get("name"))
                listed = Decimal(str(p.get("price") or 0))
                on_sim = str(p.get("dispense_method", "")).upper() == "SIM"

                obj = existing.get((network, code))
                if obj:
                    if obj.plan_type != plan_type:
                        obj.plan_type = plan_type
                        to_update.append(obj)
                    continue

                name = base if plan_type.lower() in base.lower() else f"{base} ({plan_type})"
                # Cost is only known for wallet plans. SIM plans: set it yourself via admin.
                cost = listed if (listed > 0 and not on_sim) else None
                if listed <= 0:
                    unpriced += 1
                to_create.append(DataPlan(
                    provider="smeplug",
                    network=network,
                    variation_code=code,
                    name=name,
                    price=listed,          # 0 means "set your selling price in the admin"
                    cost_price=cost,
                    plan_type=plan_type,
                    is_active=False,
                ))

        DataPlan.objects.bulk_create(to_create)
        DataPlan.objects.bulk_update(to_update, ["plan_type"])
        self.stdout.write(
            f"{len(to_create)} new (inactive), {len(to_update)} type-updated, "
            f"{unpriced} of the new ones have no price yet"
        )