import requests
from django.conf import settings


class PaystackAPIError(Exception):
    pass


def get_headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(*, email, amount, reference, callback_url=None, channels=None, metadata=None):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    payload = {
        "email": email,
        "amount": int(amount),
        "reference": reference,
    }

    if callback_url:
        payload["callback_url"] = callback_url
    if channels:
        payload["channels"] = channels
    if metadata:
        payload["metadata"] = metadata

    response = requests.post(url, json=payload, headers=get_headers(), timeout=30)
    data = response.json()

    if not response.ok or not data.get("status"):
        raise PaystackAPIError(data.get("message", "Unable to initialize Paystack transaction."))

    return data["data"]


def verify_transaction(reference):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    response = requests.get(url, headers=get_headers(), timeout=30)
    data = response.json()

    if not response.ok or not data.get("status"):
        raise PaystackAPIError(data.get("message", "Unable to verify Paystack transaction."))

    return data["data"]