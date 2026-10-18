import requests
from django.conf import settings

SERVICE_IDS = {
    "mtn": "mtn",
    "glo": "glo",
    "airtel": "airtel",
    "9mobile": "etisalat",
}

TIMEOUT = 30


def _result(outcome, provider_reference="", raw=None):
    return {"outcome": outcome, "provider_reference": provider_reference, "raw": raw}


def _headers():
    return {
        "api-key": settings.VTPASS_API_KEY,
        "secret-key": settings.VTPASS_SECRET_KEY,
    }


def _interpret(data):
    code = str(data.get("code", ""))
    txn = (data.get("content") or {}).get("transactions") or {}
    status = str(txn.get("status", "")).lower()
    ref = str(txn.get("transactionId", ""))

    if code == "000" and status == "delivered":
        return _result("success", ref, data)
    if code == "016" or status == "failed":
        return _result("failed", ref, data)
    # Anything else (processing, initiated, unknown code) is NOT a confirmed failure
    return _result("pending", ref, data)


def buy_airtime(*, network, phone, amount, reference):
    payload = {
        "request_id": reference,
        "serviceID": SERVICE_IDS[network],
        "amount": int(amount),
        "phone": phone,
    }
    try:
        resp = requests.post(
            f"{settings.VTPASS_BASE_URL}/pay",
            json=payload, headers=_headers(), timeout=TIMEOUT,
        )
        data = resp.json()
    except (requests.RequestException, ValueError):
        # Timeout, network error, or unreadable reply: we don't know what happened
        return _result("pending", "", None)
    return _interpret(data)