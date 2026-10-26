from django.contrib import admin, messages

from wallet.services import credit_wallet
from .models import FundingRequest


@admin.register(FundingRequest)
class FundingRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "amount", "amount_received", "status", "reference")
    list_filter = ("status",)
    search_fields = ("reference", "user__username", "user__email")
    readonly_fields = [f.name for f in FundingRequest._meta.fields]
    actions = ["credit_reviewed"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Credit selected REVIEW requests with the amount RECEIVED")
    def credit_reviewed(self, request, queryset):
        done = 0
        for f in queryset.filter(status=FundingRequest.Status.REVIEW):
            if not f.amount_received:
                continue
            credit_wallet(
                wallet_id=f.user.wallet.id,
                amount=f.amount_received,
                provider="paystack",
                reference=f.reference,
            )
            f.status = FundingRequest.Status.SUCCESS
            f.save(update_fields=["status", "updated_at"])
            done += 1
        self.message_user(request, f"{done} credited.", messages.SUCCESS)

# Register your models here.
