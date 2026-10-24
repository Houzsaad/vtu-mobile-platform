from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from providers import get_provider
from wallet.models import Transaction
from wallet.services import settle_transaction


class Command(BaseCommand):
    help = "Re-check PENDING transactions with thier and settle clear results."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=2)
        pending = Transaction.objects.filter(
            status=Transaction.Status.PENDING,
            type__in=[Transaction.Type.AIRTIME, Transaction.Type.DATA],
            created_at__lte=cutoff,
        )

        for txn in pending:
            result = get_provider(txn.provider).requery(txn.reference)
            if result['outcome'] in ('success', 'failed'):
                settle_transaction(
                    transaction_id=txn.id,
                    outcome=result['outcome'],
                    provider_reference=result['provider_reference'],
                    raw=result['raw'],
                )
                self.stdout.write(f"{txn.reference}: {result['outcome']}")
            else:
                self.stdout.write(f"{txn.reference} ({txn.provider}): still unclear, check by hand")