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
        
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=30)
    reference = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['provider', 'reference'], name='unique_provider_reference'),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='amount_positive'),
        ]

    def __str__(self):
        return f'{self.type} {self.amount} ({self.reference})'