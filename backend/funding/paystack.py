from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

MIN_EXPIRY = timedelta(minutes=15)
MAX_EXPIRY = timedelta(hours=8)


def clamp_expiry(minutes=None):
    delta = timedelta(minutes=minutes or settings.FUNDING_EXPIRY_MINUTES)
    delta = max(MIN_EXPIRY, min(delta, MAX_EXPIRY))
    return timezone.now() + delta


def _headers():
    return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}


def create_transfer_charge(*, email, amount_naira, reference, expires_at):
    """Ask Paystack for a temporary account. Returns (ok, data)."""
    body = {
        "email": email,
        "amount": str(int(round(float(amount_naira) * 100))),  # kobo
        "reference": reference,
        "bank_transfer": {
            "account_expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
    try:
        r = requests.post(f"{settings.PAYSTACK_BASE_URL}/charge", json=body, headers=_headers(), timeout=20)
        data = r.json()
    except (requests.RequestException, ValueError):
        return False, {}
    return bool(data.get("status")) and r.ok, data