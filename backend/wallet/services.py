from decimal import Decimal

from django.db import IntegrityError, transaction as db_transaction

from .models import Transaction, Wallet, WalletEntry

import uuid
from zoneinfo import ZoneInfo

from django.utils import timezone

def generate_reference():
    # VTPass wants request_id to start with YYYYMMDDHHmm in Lagos time
    now = timezone.now().astimezone(ZoneInfo("Africa/Lagos"))
    return now.strftime("%Y%m%d%H%M") + uuid.uuid4().hex[:12]

class DuplicateReferenceMismatch(Exception):
    """Same provider+reference was already used for a different wallet, amount or type."""
def _existing_or_raise(txn, wallet_id, amount, txn_type, recipient=''):
    if (txn.wallet_id != wallet_id or txn.amount != amount
            or txn.type != txn_type or txn.recipient != recipient):
        raise DuplicateReferenceMismatch(
            f'Reference {txn.provider}/{txn.reference} already used with different details'
        )
    return txn, False

def credit_wallet(*, wallet_id, amount, provider, reference):
    amount = Decimal(str(amount))
    if amount <= 0 or amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Amount must be positive with at most 2 decimal places')

    try:
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)

            existing = Transaction.objects.filter(provider=provider, reference=reference).first()
            if existing:
                return _existing_or_raise(existing, wallet_id, amount, Transaction.Type.DEPOSIT)

            balance_before = wallet.balance
            wallet.balance += amount
            wallet.save(update_fields=['balance', 'updated_at'])

            txn = Transaction.objects.create(
                wallet=wallet,
                type=Transaction.Type.DEPOSIT,
                amount=amount,
                balance_after=wallet.balance,
                provider=provider,
                reference=reference,
                status=Transaction.Status.SUCCESS,
            )
            WalletEntry.objects.create(
                wallet=wallet,
                transaction=txn,
                kind=WalletEntry.Kind.CREDIT,
                amount=amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
            )
            return txn, True
    except IntegrityError:
        # Lost a race (e.g. same reference sent to a different wallet at the same time).
        # The whole block rolled back, so no money moved. Re-check what won.
        existing = Transaction.objects.filter(provider=provider, reference=reference).first()
        if existing is None:
            raise
        return _existing_or_raise(existing, wallet_id, amount, Transaction.Type.DEPOSIT)

class InsufficientFunds(Exception):
    """Wallet balance is lower than the purchase amount."""


def debit_wallet(*, wallet_id, amount, txn_type, recipient, provider, reference, network=''):
    if txn_type not in (Transaction.Type.AIRTIME, Transaction.Type.DATA):
        raise ValueError('txn_type must be airtime or data')

    recipient = str(recipient).strip()
    if not recipient:
        raise ValueError('Recipient phone number is required')
    
  
    amount = Decimal(str(amount))
    if amount <= 0 or amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Amount must be positive with at most 2 decimal places')

    try:
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)

            existing = Transaction.objects.filter(provider=provider, reference=reference).first()
            if existing:
                return _existing_or_raise(existing, wallet_id, amount, txn_type, recipient)

            if wallet.balance < amount:
                raise InsufficientFunds('Insufficient wallet balance')

            balance_before = wallet.balance
            wallet.balance -= amount
            wallet.save(update_fields=['balance', 'updated_at'])

            txn = Transaction.objects.create(
                wallet=wallet,
                type=txn_type,
                amount=amount,
                balance_after=wallet.balance,
                provider=provider,
                reference=reference,
                recipient=recipient,
                network=network,
                status=Transaction.Status.PENDING,
            )
            WalletEntry.objects.create(
                wallet=wallet,
                transaction=txn,
                kind=WalletEntry.Kind.DEBIT,
                amount=amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
            )
            return txn, True
    except IntegrityError:
        existing = Transaction.objects.filter(provider=provider, reference=reference).first()
        if existing is None:
            raise
        return _existing_or_raise(existing, wallet_id, amount, txn_type, recipient)
    

def settle_transaction(*, transaction_id, outcome, provider_reference='', raw=None):
    with db_transaction.atomic():
        txn = Transaction.objects.select_for_update().get(pk=transaction_id)

        # Already final: never change a settled transaction
        if txn.status != Transaction.Status.PENDING:
            return txn

        if provider_reference:
            txn.provider_reference = provider_reference
        if raw is not None:
            txn.provider_response = raw

        if outcome == 'success':
            txn.status = Transaction.Status.SUCCESS

        elif outcome == 'failed':
            txn.status = Transaction.Status.FAILED
            if not txn.refunded:
                wallet = Wallet.objects.select_for_update().get(pk=txn.wallet_id)
                balance_before = wallet.balance
                wallet.balance += txn.amount
                wallet.save(update_fields=['balance', 'updated_at'])
                WalletEntry.objects.create(
                    wallet=wallet,
                    transaction=txn,
                    kind=WalletEntry.Kind.REFUND,
                    amount=txn.amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                )
                txn.refunded = True
        # outcome == 'pending': stay PENDING, just keep the saved response
        txn.save()
        return txn