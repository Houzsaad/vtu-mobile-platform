import json
import uuid

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print raw SMEPlug responses. Nothing is saved."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["balance", "buy", "check"])
        parser.add_argument("--network", type=int)
        parser.add_argument("--plan")
        parser.add_argument("--phone")
        parser.add_argument("--ref")

    def handle(self, *args, **o):
        base = settings.SMEPLUG_BASE_URL
        headers = {"Authorization": f"Bearer {settings.SMEPLUG_SECRET_KEY}"}

        if o["action"] == "balance":
            r = requests.get(f"{base}/account/balance", headers=headers, timeout=30)
        elif o["action"] == "check":
            r = requests.get(f"{base}/transactions/{o['ref']}", headers=headers, timeout=30)
        else:
            ref = uuid.uuid4().hex[:20]
            self.stdout.write(f"customer_reference: {ref}")
            r = requests.post(
                f"{base}/data/purchase",
                headers=headers,
                json={
                    "network_id": o["network"],
                    "plan_id": o["plan"],
                    "phone": o["phone"],
                    "customer_reference": ref,
                },
                timeout=60,
            )

        self.stdout.write(f"HTTP {r.status_code}")
        try:
            body = r.json()
            if isinstance(body, dict):
                body.pop("initiator", None)
            self.stdout.write(json.dumps(body, indent=2))
        except ValueError:
            self.stdout.write(r.text[:500])