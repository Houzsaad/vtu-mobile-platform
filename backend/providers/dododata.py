import re

import requests
from django.conf import settings
from decimal import Decimal, InvalidOperation


NETWORK_IDS = {"mtn": "1", "airtel": "2", "9mobile": "3", "glo": "4"}
TIMEOUT = 30

def _balance_unchanged(data):
    try:
        return Decimal(str(data["balance_before"])) == Decimal(str(data["balance_after"]))
    except (KeyError, InvalidOperation):
        return False

def _result(outcome, provider_reference="", raw=None):
    return {"outcome": outcome, "provider_reference": provider_reference, "raw": raw}


def _headers():
    return {
        "Authorization": f"Token {settings.DODODATA_API_KEY}",
        "Content-Type": "application/json",
    }


def _interpret(resp):
    try:
        data = resp.json()
    except ValueError:
        data = None

    ref = ""
    if isinstance(data, dict):
        match = re.search(r"TRX ID:\s*([\w-]+)", str(data.get("api_response", "")))
        ref = match.group(1) if match else ""
        raw = {**data, "_http_status": resp.status_code}
    else:
        raw = {"_http_status": resp.status_code, "text": resp.text[:500]}

    if (resp.status_code == 200 and isinstance(data, dict)
            and str(data.get("status", "")).lower() == "success"):
        return _result("success", ref, raw)
    if resp.status_code in (400, 401, 403):
        # Request refused before processing, so nothing was bought
        return _result("failed", "", raw)

    if (resp.status_code == 200 and isinstance(data, dict)
            and str(data.get("status", "")).lower() in ("fail", "failed")
            and _balance_unchanged(data)):
        # DodoData says fail and took no money, so the user can be refunded
        return _result("failed", "", raw)
    
    # Everything else (timeouts, 409, 429, 5xx, unknown replies) is NOT a confirmed failure
    return _result("pending", ref, raw)


def buy_airtime(*, network, phone, amount, reference):
    # DodoData's docs show no field for our own reference
    payload = {"network": NETWORK_IDS[network], "phone": phone, "amount": int(amount)}
    try:
        resp = requests.post(
            f"{settings.DODODATA_BASE_URL}/api/topup",
            json=payload, headers=_headers(), timeout=TIMEOUT,
        )
    except requests.RequestException:
        return _result("pending")
    return _interpret(resp)


def requery(reference):
    # No status endpoint is documented, so this can never confirm anything
    return _result("pending")

def buy_data(*, network, phone, variation_code, reference):
    # variation_code holds DodoData's numeric plan ID
    payload = {
        "network": int(NETWORK_IDS[network]),
        "mobile_number": phone,
        "plan": int(variation_code),
        "Ported_number": False,
    }
    try:
        resp = requests.post(
            f"{settings.DODODATA_BASE_URL}/api/data",
            json=payload, headers=_headers(), timeout=TIMEOUT,
        )
    except requests.RequestException:
        return _result("pending")
    return _interpret(resp)