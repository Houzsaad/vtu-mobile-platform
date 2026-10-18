from django.conf import settings
from importlib import import_module

def get_provider():
    return import_module(f"providers.{settings.VTU_PROVIDER}")