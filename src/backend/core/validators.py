"""
Declare validators that can be used in our Django models.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def get_field_validators_from_setting(setting_name: str) -> list:
    """
    Get field validators from a setting.

    Highly inspired by Django's `get_password_validators` function.

    The setting should be a list of dictionaries, where each dictionary
    should have a NAME key that points to the validator class and an
    optional OPTIONS key that points to the validator options.

    Example:
    ```
    ORGANIZATION_REGISTRATION_ID_VALIDATORS = [
        {
            "NAME": "django.core.validators.RegexValidator",
            "OPTIONS": {
                "regex": "[a-z][0-9]{14}",
            },
        },
    ]
    ```
    """
    validators = []
    for validator in getattr(settings, setting_name):
        try:
            klass = import_string(validator["NAME"])
        except ImportError as exc:
            msg = "The module in NAME could not be imported: %s. Check your %s setting."
            raise ImproperlyConfigured(msg % (validator["NAME"], setting_name)) from exc
        validators.append(klass(**validator.get("OPTIONS", {})))

    return validators
