from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

from .validators import validate_full_name, validate_username



import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^(090|091|080|081|070)\d{8}$',
    message="Phone number must be 11 digits, starting with 090/091/080/081/070."
)


class User(AbstractUser):
    full_name = models.CharField(max_length=150, validators=[validate_full_name] )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=11, validators=[phone_validator]
    )
    pin_hash = models.CharField(max_length=128, blank=True, null=True)

    def set_pin(self, raw_pin):
        self.pin_hash = make_password(raw_pin)

    def check_pin(self, raw_pin):
        if not self.pin_hash:
            return False
        return check_password(raw_pin, self.pin_hash)

    def __str__(self):
        return self.username


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD_RESET = "password_reset", "Password reset"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_codes")
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    MAX_ATTEMPTS = 5
    LIFETIME = timedelta(minutes=10)

    @staticmethod
    def _hash(code):
        return hmac.new(settings.SECRET_KEY.encode(), code.encode(), hashlib.sha256).hexdigest()

    @classmethod
    def issue(cls, user, purpose):
        """Create a fresh code, cancel older ones, return the plain code once."""
        cls.objects.filter(user=user, purpose=purpose, used_at__isnull=True)\
            .update(used_at=timezone.now())
        code = f"{secrets.randbelow(1_000_000):06d}"
        cls.objects.create(user=user, purpose=purpose, code_hash=cls._hash(code), expires_at=timezone.now() + cls.LIFETIME)
        return code

    @classmethod
    def verify(cls, user, purpose, code):
        """True once if the code is right, unused, unexpired and attempts remain."""
        otp = (cls.objects.filter(user=user, purpose=purpose, used_at__isnull=True)
               .order_by("-created_at").first())
        if not otp or otp.expires_at < timezone.now() or otp.attempts >= cls.MAX_ATTEMPTS:
            return False
        otp.attempts += 1
        if not hmac.compare_digest(otp.code_hash, cls._hash(str(code))):
            otp.save(update_fields=["attempts"])
            return False
        otp.used_at = timezone.now()
        otp.save(update_fields=["attempts", "used_at"])
        return True

# Create your models here.


