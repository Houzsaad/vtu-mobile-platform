from rest_framework import serializers

from .models import Transaction, DataPlan

from django.contrib import admin, messages
from .services import settle_transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'balance_after', 'recipient', 'reference', 'created_at', "status", "refunded"]
        read_only_fields = fields

actions = ["mark_success", "mark_failed_refund"]

@admin.action(description="Mark selected PENDING as SUCCESS")
def mark_success(self, request, queryset):
    done = 0
    for txn in queryset.filter(status="pending"):
        settle_transaction(txn.id, "success", raw={"settled_by": request.user.username})
        done += 1
    self.message_user(request, f"{done} marked success.", messages.SUCCESS)

@admin.action(description="Mark selected PENDING as FAILED and refund")
def mark_failed_refund(self, request, queryset):
    done = 0
    for txn in queryset.filter(status="pending"):
        settle_transaction(txn.id, "failed", raw={"settled_by": request.user.username})
        done += 1
    self.message_user(request, f"{done} marked failed and refunded.", messages.SUCCESS)


PHONE_REGEX = r'^(090|091|080|081|070)\d{8}$'

class AirtimePurchaseSerializer(serializers.Serializer):
    network = serializers.ChoiceField(choices=Transaction.Network.choices)
    phone = serializers.RegexField(PHONE_REGEX)
    amount = serializers.IntegerField(min_value=50, max_value=50000)
    pin = serializers.RegexField(r'^\d{4}$')



class DataPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPlan
        fields = ['id', 'network', 'name', 'price']


class DataPurchaseSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(min_value=1)
    phone = serializers.RegexField(PHONE_REGEX)
    pin = serializers.RegexField(r'^\d{4}$')