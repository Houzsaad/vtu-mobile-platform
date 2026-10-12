from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Transaction
from .services import DuplicateReferenceMismatch, credit_wallet

from .services import DuplicateReferenceMismatch, InsufficientFunds, credit_wallet, debit_wallet

from rest_framework.test import APIClient

User = get_user_model()


class CreditWalletTests(TestCase):
    
    def make_wallet(self, n):
        user = User.objects.create_user(
            username=f'user{n}', email=f'user{n}@test.com', password='Test1234!',
            full_name=f'User{n}', phone_number=f'0801234567{n}',
        )
        return user.wallet

    def setUp(self):
        self.w1 = self.make_wallet(1)
        self.w2 = self.make_wallet(2)

    def credit(self, wallet, amount='500.00', ref='p1'):
        return credit_wallet(wallet_id=wallet.id, amount=amount, provider='test', reference=ref)

    def test_credit_adds_balance_and_ledger_row(self):
        txn, created = self.credit(self.w1)
        self.w1.refresh_from_db()
        self.assertTrue(created)
        self.assertEqual(self.w1.balance, Decimal('500.00'))
        self.assertEqual(txn.balance_after, Decimal('500.00'))

    def test_same_reference_is_credited_once(self):
        self.credit(self.w1)
        _, created = self.credit(self.w1)
        self.w1.refresh_from_db()
        self.assertFalse(created)
        self.assertEqual(self.w1.balance, Decimal('500.00'))
        self.assertEqual(Transaction.objects.count(), 1)

    def test_same_reference_different_amount_is_blocked(self):
        self.credit(self.w1)
        with self.assertRaises(DuplicateReferenceMismatch):
            self.credit(self.w1, amount='900.00')

    def test_same_reference_different_wallet_is_blocked(self):
        self.credit(self.w1)
        with self.assertRaises(DuplicateReferenceMismatch):
            self.credit(self.w2)
        self.w2.refresh_from_db()
        self.assertEqual(self.w2.balance, Decimal('0.00'))

    def test_bad_amounts_rejected(self):
        for bad in ('0', '-5', '10.005'):
            with self.assertRaises(ValueError):
                self.credit(self.w1, amount=bad, ref=f'bad{bad}')
    
    def debit(self, wallet, amount='200.00', ref='buy1', txn_type=Transaction.Type.AIRTIME):
        return debit_wallet(
            wallet_id=wallet.id, amount=amount, txn_type=txn_type, provider='vtpass', reference=ref
        )

    def test_debit_reduces_balance_and_writes_ledger_row(self):
        self.credit(self.w1)
        txn, created = self.debit(self.w1)
        self.w1.refresh_from_db()
        self.assertTrue(created)
        self.assertEqual(self.w1.balance, Decimal('300.00'))
        self.assertEqual(txn.type, Transaction.Type.AIRTIME)
        self.assertEqual(txn.balance_after, Decimal('300.00'))

    def test_debit_cannot_exceed_balance(self):
        self.credit(self.w1, amount='100.00')
        with self.assertRaises(InsufficientFunds):
            self.debit(self.w1, amount='200.00')
        self.w1.refresh_from_db()
        self.assertEqual(self.w1.balance, Decimal('100.00'))
        self.assertEqual(Transaction.objects.filter(type=Transaction.Type.AIRTIME).count(), 0)

    def test_same_purchase_reference_debits_once(self):
        self.credit(self.w1)
        self.debit(self.w1)
        _, created = self.debit(self.w1)
        self.w1.refresh_from_db()
        self.assertFalse(created)
        self.assertEqual(self.w1.balance, Decimal('300.00'))

    def test_same_purchase_reference_different_amount_is_blocked(self):
        self.credit(self.w1)
        self.debit(self.w1)
        with self.assertRaises(DuplicateReferenceMismatch):
            self.debit(self.w1, amount='250.00')

    def test_debit_rejects_deposit_type(self):
        self.credit(self.w1)
        with self.assertRaises(ValueError):
            self.debit(self.w1, txn_type=Transaction.Type.DEPOSIT)

class TransactionHistoryTests(CreditWalletTests):
    def test_user_sees_only_own_transactions(self):
        self.credit(self.w1, ref='mine')
        self.credit(self.w2, ref='theirs')

        client = APIClient()
        client.force_authenticate(user=self.w1.user)
        response = client.get('/api/wallet/transactions/')

        self.assertEqual(response.status_code, 200)
        references = [row['reference'] for row in response.data['results']]
        self.assertEqual(references, ['mine'])

    def test_history_requires_login(self):
        response = APIClient().get('/api/wallet/transactions/')
        self.assertEqual(response.status_code, 401)

# Create your tests here.
