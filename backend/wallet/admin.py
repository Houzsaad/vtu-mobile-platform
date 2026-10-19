
from django.contrib import admin
from .models import Wallet, Transaction, DataPlan

from decimal import Decimal, InvalidOperation

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm

from .models import Wallet
from .services import credit_wallet, generate_reference


# @admin.register(Wallet)
# class WalletAdmin(admin.ModelAdmin):
#     list_display = ("id", "user", "balance")
#     search_fields = ("user__username", "user__email")
#     readonly_fields = ("user", "balance")
#     ordering = ("-id",)


class FundActionForm(ActionForm):
    amount = forms.DecimalField(required=False, label='Amount (₦)')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    readonly_fields = ('user', 'balance', 'created_at', 'updated_at')
    action_form = FundActionForm
    actions = ['test_fund']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='TEST: fund selected wallets')
    def test_fund(self, request, queryset):
        if not settings.ALLOW_TEST_FUNDING:
            self.message_user(request, 'Test funding is disabled.', messages.ERROR)
            return
        try:
            amount = Decimal(request.POST.get('amount', ''))
        except InvalidOperation:
            self.message_user(request, 'Enter an amount first.', messages.ERROR)
            return
        if amount <= 0:
            self.message_user(request, 'Amount must be above zero.', messages.ERROR)
            return

        for wallet in queryset:
            credit_wallet(
                wallet_id=wallet.id,
                amount=amount,
                provider='admin-test',
                reference=generate_reference(),
            )
        self.message_user(request, f'Funded {queryset.count()} wallet(s) with ₦{amount}.')

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
        # "wallet",
        "type",
        "amount",
        "balance_after",
        "provider",
        "reference",
    )
    ordering = ("-id",)



@admin.register(DataPlan)
class DataPlanAdmin(admin.ModelAdmin):
    list_display = ('network', 'name', 'variation_code', 'price', 'is_active')
    list_editable = ('price', 'is_active')
    list_filter = ('network', 'is_active')

# Register your models here.
