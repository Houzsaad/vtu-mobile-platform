from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from .validators import validate_full_name, validate_username
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from wallet.models import Wallet


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    confirm_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    full_name = serializers.CharField(validators=[validate_full_name])
    username = serializers.CharField(validators=[validate_username])

    class Meta:
        model = User
        fields = [
            'full_name', 'username', 'email', 'phone_number',
            'password', 'confirm_password', 'pin', 'confirm_pin',
        ]

      #  read_only_fields = ['username', 'email', 'pin', 'wallet', 'passsord']

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numbers.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if data['pin'] != data['confirm_pin']:
            raise serializers.ValidationError({"confirm_pin": "PINs do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('confirm_pin')
        pin = validated_data.pop('pin')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.set_pin(pin)
        user.save()
        return user



class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        data['full_name'] = self.user.full_name
        data['username'] = self.user.username
        data['wallet_balance'] = str(self.user.wallet.balance)
        return data

class ProfileSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'phone_number', 'wallet_balance']

    def get_wallet_balance(self, obj):
        return str(obj.wallet.balance)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Passwords doesn't match."})
        return data

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        user = self.context['request'].user
        if user.check_password(data['new_password']):
            raise serializers.ValidationError({"new_password": "New password cannot be the same as your current password."})
        return data    

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class ChangePinSerializer(serializers.Serializer):
    current_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    new_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)
    confirm_new_pin = serializers.CharField(write_only=True, min_length=4, max_length=4)

    def validate_current_pin(self, value):
        user = self.context['request'].user
        if not user.check_pin(value):
            raise serializers.ValidationError("Current PIN is incorrect.")
        return value

    def validate_new_pin(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numbers.")
        return value

    def validate(self, data):
        if data['new_pin'] != data['confirm_new_pin']:
            raise serializers.ValidationError({"confirm_new_pin": "PINs do not match."})
        return data

    def validate(self, data):
        if data['new_pin'] != data['confirm_new_pin']:
            raise serializers.ValidationError({"confirm_new_pin": "PINs do not match."})
        user = self.context['request'].user
        if user.check_pin(data['new_pin']):
            raise serializers.ValidationError({"new_pin": "New PIN cannot be the same as your current PIN."})
        return data

    def save(self):
        user = self.context['request'].user
        user.set_pin(self.validated_data['new_pin'])
        user.save()
        return user