import time
import requests
from django.conf import settings

NETWORK_IDS = {"mtn": 1, "airtel": 2, "9mobile": 3, "glo": 4}
BUY_TIMEOUT = 60   # a SIM can be slow
CHECK_TIMEOUT = 30


def _headers():
    return {"Authorization": f"Bearer {settings.SMEPLUG_SECRET_KEY}"}


def _result(outcome, provider_reference="", raw=None):
    return {"outcome": outcome, "provider_reference": provider_reference, "raw": raw}


def _trim(http_status, body):
    """Keep only what we need. Never store the whole reply (it can hold account details)."""
    if not isinstance(body, dict):
        return {"_http_status": http_status}
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    return {
        "_http_status": http_status,
        "status": body.get("status"),
        "current_status": data.get("current_status"),
        "msg": data.get("msg") or body.get("msg") or body.get("response"),
        "amount": data.get("amount") if data else body.get("price"),
    }


def interpret(http_status, body, *, trust_rejection=True):
    """Return (outcome, message). outcome: 'success', 'failed' or 'pending'."""
    if not isinstance(body, dict):
        return "pending", "Unreadable reply"

    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    state = str(data.get("current_status") or "").lower()
    message = data.get("msg") or body.get("msg") or body.get("response") or ""

    # Buy reply: status true + current_status success
    if body.get("status") is True and state == "success":
        return "success", message

    # Requery reply: status is a word such as "Success" / "Failed"
    if isinstance(body.get("status"), str):
        word = body["status"].lower()
        if word == "success":
            return "success", message
        if word == "failed":
            return "failed", message

    # Explicit failure from the SIM or network
    if state == "failed":
        return "failed", message

    # Rejected before anything was sent. Only trusted on a buy, never on a requery.
    if (trust_rejection and body.get("status") is False and not state
            and http_status in (400, 401, 403, 404, 422)):
        return "failed", message

    # Timeouts, 5xx, "processing", unknown replies: leave for review
    return "pending", message


def _provider_ref(body):
    if not isinstance(body, dict):
        return ""
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    return str(data.get("reference") or body.get("ref") or body.get("reference") or "")


def buy_data(*, network, phone, variation_code, reference):
    payload = {
        "network_id": NETWORK_IDS[network],
        "plan_id": str(variation_code),
        "phone": phone,
        "customer_reference": reference,
    }
    try:
        resp = requests.post(
            f"{settings.SMEPLUG_BASE_URL}/data/purchase",
            json=payload, headers=_headers(), timeout=BUY_TIMEOUT,
        )
    except requests.RequestException:
        return _result("pending")   # unknown, never refund on a timeout
    try:
        body = resp.json()
    except ValueError:
        body = None
    outcome, _ = interpret(resp.status_code, body)
    return _result(outcome, _provider_ref(body), _trim(resp.status_code, body))


def requery(reference):
    try:
        resp = requests.get(
            f"{settings.SMEPLUG_BASE_URL}/transactions/{reference}",
            headers=_headers(), timeout=CHECK_TIMEOUT,
        )
        body = resp.json()
    except (requests.RequestException, ValueError):
        return _result("pending")
    outcome, _ = interpret(resp.status_code, body, trust_rejection=False)
    return _result(outcome, _provider_ref(body), _trim(resp.status_code, body))



def buy_airtime(*, network, phone, amount, reference):
    payload = {
        "network_id": NETWORK_IDS[network],
        "phone": phone,
        "amount": int(amount),
        "customer_reference": reference,
    }
    try:
        resp = requests.post(
            f"{settings.SMEPLUG_BASE_URL}/airtime/purchase",
            json=payload, headers=_headers(), timeout=BUY_TIMEOUT,
        )
    except requests.RequestException:
        return _result("pending")   # unknown, never refund on a timeout
    try:
        body = resp.json()
    except ValueError:
        body = None

    outcome, _ = interpret(resp.status_code, body)
    provider_ref = _provider_ref(body)

    # Accepted but not confirmed: ask SMEPlug a few times, using their own reference
    if outcome == "pending" and provider_ref and isinstance(body, dict) and body.get("status") is True:
        for _ in range(3):
            time.sleep(2)
            check = requery(provider_ref)
            if check["outcome"] != "pending":
                return check
    return _result(outcome, provider_ref, _trim(resp.status_code, body))