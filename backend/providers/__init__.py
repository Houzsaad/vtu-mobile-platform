from importlib import import_module

from django.conf import settings


def get_provider(name=None):
    return import_module(f"providers.{name or settings.VTU_PROVIDER}")