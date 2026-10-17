
from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "balance")
    ordering = ("-id",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "type",
        "amount",
        "balance_after",
        "provider",
        "reference",
    )
    search_fields = (
        "wallet__user__username",
        "wallet__user__email",
        "reference",
        "provider",
    )
    list_filter = ("type", "provider")
    readonly_fields = (
        "wallet",
        "type",
        "amount",
        "balance_after",
        "provider",
        "reference",
    )
    ordering = ("-id",)

# Register your models here.
