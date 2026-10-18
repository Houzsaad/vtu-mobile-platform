from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s wallet — ₦{self.balance}"


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit'
        AIRTIME = 'airtime', 'Airtime'
        DATA = 'data', 'Data'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    class Network(models.TextChoices):
        MTN = 'mtn', 'MTN'
        GLO = 'glo', 'Glo'
        AIRTEL = 'airtel', 'Airtel'
        NINE_MOBILE = '9mobile', '9mobile'

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    network = models.CharField(max_length=10, choices=Network.choices, blank=True)
    provider_reference = models.CharField(max_length=100, blank=True)
    provider_response = models.JSONField(null=True, blank=True)
    refunded = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
        
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=30)
    reference = models.CharField(max_length=100)
    recipient = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['provider', 'reference'], name='unique_provider_reference'),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='amount_positive'),
        ]

    def __str__(self):
        return f'{self.type} {self.amount} ({self.reference})'

class WalletEntry(models.Model):
    class Kind(models.TextChoices):
        DEBIT = 'debit', 'Debit'
        REFUND = 'refund', 'Refund'
        CREDIT = 'credit', 'Credit'

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='entries')
    transaction = models.ForeignKey(
        Transaction, on_delete=models.PROTECT, related_name='entries'
    )
    kind = models.CharField(max_length=10, choices=Kind.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['transaction', 'kind'], name='one_entry_per_kind_per_transaction'
            ),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='entry_amount_positive'),
        ]

    def __str__(self):
        return f'{self.kind} {self.amount} for {self.transaction.reference}'