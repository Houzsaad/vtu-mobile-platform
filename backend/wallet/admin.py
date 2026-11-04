from decimal import Decimal, InvalidOperation

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm

from .models import DataPlan, Transaction, Wallet, WalletEntry
from .services import credit_wallet, generate_reference, refund_failed, settle_transaction


class FundActionForm(ActionForm):
    amount = forms.DecimalField(required=False, label='Amount (₦)')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__email')
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
        'id', 'created_at', 'wallet', 'type', 'amount',
        'status', 'refunded', 'recipient', 'provider', 'reference',
    )
    search_fields = (
        'wallet__user__username', 'wallet__user__email',
        'reference', 'provider_reference', 'recipient',
    )
    list_filter = ('status', 'refunded', 'type', 'provider')
    # Every field is read-only: status changes must go through the actions below,
    # because only they move money correctly.
    readonly_fields = [f.name for f in Transaction._meta.fields]
    ordering = ('-id',)
    actions = ['mark_success', 'mark_failed_refund']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Mark selected PENDING as SUCCESS')
    def mark_success(self, request, queryset):
        done = 0
        for txn in queryset.filter(status=Transaction.Status.PENDING):
            settle_transaction(transaction_id=txn.id, outcome='success')
            done += 1
        self.message_user(request, f'{done} marked success.', messages.SUCCESS)

    @admin.action(description='Mark selected PENDING as FAILED and refund')
    def mark_failed_refund(self, request, queryset):
        done = 0
        for txn in queryset.filter(status__in=[Transaction.Status.PENDING, Transaction.Status.FAILED]):
            if txn.status == Transaction.Status.PENDING:
                settle_transaction(transaction_id=txn.id, outcome='failed')
            refund_failed(transaction_id=txn.id)  # also repairs FAILED rows that were never refunded
            done += 1
        self.message_user(request, f'{done} processed (failed and refunded).', messages.SUCCESS)


@admin.register(WalletEntry)
class WalletEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'wallet', 'transaction', 'kind', 'amount',
                    'balance_before', 'balance_after')
    list_filter = ('kind',)
    search_fields = ('transaction__reference', 'wallet__user__username')
    readonly_fields = [f.name for f in WalletEntry._meta.fields]
    ordering = ('-id',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DataPlan)
class DataPlanAdmin(admin.ModelAdmin):
    list_display = ('provider', 'network', 'plan_type', 'name', 'variation_code',
                    'cost_price', 'price', 'is_active')
    list_editable = ('price', 'is_active')
    list_filter = ('provider', 'network', 'plan_type', 'is_active')
    search_fields = ('name', 'variation_code')
    actions = ['activate_plans', 'deactivate_plans']

    @admin.action(description='Activate selected plans')
    def activate_plans(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_active=True)} activated.')

    @admin.action(description='Deactivate selected plans')
    def deactivate_plans(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_active=False)} deactivated.')