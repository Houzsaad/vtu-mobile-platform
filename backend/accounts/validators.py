import re
from django.core.exceptions import ValidationError


def validate_full_name(value):
    if not re.match(r"^[A-Za-z' ]+$", value):
        raise ValidationError("Full name can only contain letters, spaces, and apostrophes.")


def validate_username(value):
    if not re.match(r"^[A-Za-z0-9]+$", value):
        raise ValidationError("Username can only contain letters and numbers.")


class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain a lowercase letter.", code='password_no_lower')
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain an uppercase letter.", code='password_no_upper')
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain a number.", code='password_no_number')
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError("Password must contain a special character.", code='password_no_special')

    def get_help_text(self):
        return "Password must include an uppercase letter, a lowercase letter, a number, and a special character."