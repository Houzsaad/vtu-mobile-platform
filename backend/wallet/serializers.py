from rest_framework import serializers

from .models import Transaction, DataPlan


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'balance_after', 'recipient', 'reference', 'created_at']
        read_only_fields = fields


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