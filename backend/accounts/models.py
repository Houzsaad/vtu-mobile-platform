from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

from .validators import validate_full_name, validate_username


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
    
# Create your models here.
