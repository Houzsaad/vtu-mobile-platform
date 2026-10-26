from django.conf import settings
from rest_framework import serializers

from .models import FundingRequest


class InitiateFundingSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value < settings.FUNDING_MIN_AMOUNT:
            raise serializers.ValidationError(
                f"Minimum funding is ₦{settings.FUNDING_MIN_AMOUNT}.")
        if value > settings.FUNDING_MAX_AMOUNT:
            raise serializers.ValidationError(
                f"Maximum funding is ₦{settings.FUNDING_MAX_AMOUNT}.")
        return value


class FundingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingRequest
        fields = ["reference", "amount", "status", "bank_name", "account_number", "account_name", "expires_at"]