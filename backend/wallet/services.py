from decimal import Decimal

from django.db import IntegrityError, transaction as db_transaction

from .models import Transaction, Wallet, WalletEntry, DataPlan

import uuid
from zoneinfo import ZoneInfo

from django.utils import timezone

from providers import vtpass

from django.conf import settings
from providers import get_provider

import re

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


def debit_wallet(*, wallet_id, amount, txn_type, recipient, provider, reference, network='', description=''):
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
                description=description,
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


def purchase_airtime(*, wallet_id, network, phone, amount, reference=None):
    provider_name = settings.VTU_PROVIDER
    reference = reference or generate_reference()

    # 1. Debit + PENDING transaction, committed before any provider calling external provider
    txn, created = debit_wallet(
        wallet_id=wallet_id,
        amount=amount,
        txn_type=Transaction.Type.AIRTIME,
        recipient=phone,
        provider=provider_name,
        reference=reference,
        network=network,
    )

    # A repeated reference returns the existing transaction. Never call VTPassor any provider again.
    if not created:
        return txn

    # 2. Call the provider with no database lock held
    try:
        result = get_provider(provider_name).buy_airtime(
            network=network, phone=phone, amount=amount, reference=reference
        )
    except Exception:
        # Unknown state is not a failure (golden rule)
        result = {'outcome': 'pending', 'provider_reference': '', 'raw': None}

    # 3. Settle based on what VTPass or any provider said
    return settle_transaction(
        transaction_id=txn.id,
        outcome=result['outcome'],
        provider_reference=result['provider_reference'],
        raw=result['raw'],
    )

class InvalidPin(Exception):
    pass

def verify_transaction_pin(user, pin):
    pin = str(pin)
    if not re.fullmatch(r"\d{4}", pin):
        raise InvalidPin()
    if not user.check_pin(pin):
        raise InvalidPin()



class PlanUnavailable(Exception):
    pass


def purchase_data(*, wallet_id, plan_id, phone, reference=None):
    provider_name = settings.VTU_PROVIDER
    # Law 3 and 15: the price and availability come from the database
    try:
        plan = DataPlan.objects.get(pk=plan_id, is_active=True, provider=provider_name)
    except DataPlan.DoesNotExist:
        raise PlanUnavailable()

    reference = reference or generate_reference()

    txn, created = debit_wallet(
        wallet_id=wallet_id,
        amount=plan.price,
        txn_type=Transaction.Type.DATA,
        recipient=phone,
        provider=provider_name,
        reference=reference,
        network=plan.network,
        description=plan.name,
    )

    if not created:
        return txn

    try:
        result = get_provider(provider_name).buy_data(
            network=plan.network,
            phone=phone,
            variation_code=plan.variation_code,
            reference=reference,
        )
    except Exception:
        result = {'outcome': 'pending', 'provider_reference': '', 'raw': None}

    return settle_transaction(
        transaction_id=txn.id,
        outcome=result['outcome'],
        provider_reference=result['provider_reference'],
        raw=result['raw'],
    )