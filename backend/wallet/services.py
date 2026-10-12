from decimal import Decimal

from django.db import IntegrityError, transaction as db_transaction

from .models import Transaction, Wallet


class DuplicateReferenceMismatch(Exception):
    """Same provider+reference was already used for a different wallet, amount or type."""

def _existing_or_raise(txn, wallet_id, amount, txn_type):
    if txn.wallet_id != wallet_id or txn.amount != amount or txn.type != txn_type:
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

            wallet.balance += amount
            wallet.save(update_fields=['balance'])

            txn = Transaction.objects.create(
                wallet=wallet,
                type=Transaction.Type.DEPOSIT,
                amount=amount,
                balance_after=wallet.balance,
                provider=provider,
                reference=reference,
            )
            return txn, True
    except IntegrityError:
        # Lost a race (e.g. same reference sent to a different wallet at the same time).
        # The whole block rolled back, so no money moved. Re-check what won.
        existing = Transaction.objects.filter(provider=provider, reference=reference).first()
        if existing is None:
            raise
        return _existing_or_raise(existing, wallet_id, amount)

class InsufficientFunds(Exception):
    """Wallet balance is lower than the purchase amount."""


def debit_wallet(*, wallet_id, amount, txn_type, provider, reference):
    if txn_type not in (Transaction.Type.AIRTIME, Transaction.Type.DATA):
        raise ValueError('txn_type must be airtime or data')

    amount = Decimal(str(amount))
    if amount <= 0 or amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Amount must be positive with at most 2 decimal places')

    try:
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=wallet_id)

            existing = Transaction.objects.filter(provider=provider, reference=reference).first()
            if existing:
                return _existing_or_raise(existing, wallet_id, amount, txn_type)

            if wallet.balance < amount:
                raise InsufficientFunds('Insufficient wallet balance')

            wallet.balance -= amount
            wallet.save(update_fields=['balance'])

            txn = Transaction.objects.create(
                wallet=wallet,
                type=txn_type,
                amount=amount,
                balance_after=wallet.balance,
                provider=provider,
                reference=reference,
            )
            return txn, True
    except IntegrityError:
        existing = Transaction.objects.filter(provider=provider, reference=reference).first()
        if existing is None:
            raise
        return _existing_or_raise(existing, wallet_id, amount, txn_type)