from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from providers import vtpass
from wallet.models import Transaction
from wallet.services import settle_transaction


class Command(BaseCommand):
    help = "Re-check PENDING transactions with VTPass and settle clear results."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=2)
        pending = Transaction.objects.filter(
            status=Transaction.Status.PENDING,
            provider='vtpass',
            created_at__lte=cutoff,
        )

        for txn in pending:
            result = vtpass.requery(txn.reference)
            if result['outcome'] in ('success', 'failed'):
                settle_transaction(
                    transaction_id=txn.id,
                    outcome=result['outcome'],
                    provider_reference=result['provider_reference'],
                    raw=result['raw'],
                )
                self.stdout.write(f"{txn.reference}: {result['outcome']}")
            else:
                self.stdout.write(f"{txn.reference}: still unclear, check by hand")