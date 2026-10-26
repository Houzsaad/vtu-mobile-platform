import uuid
from django.conf import settings
from django.db import models


class FundingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        EXPIRED = "expired", "Expired"
        REVIEW = "review", "Needs review"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="funding_requests")
    reference = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)

    # Filled in from Paystack
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=150, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    amount_received = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} · ₦{self.amount} · {self.status}"

# Create your models here.
