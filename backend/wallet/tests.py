from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Transaction
from .services import DuplicateReferenceMismatch, credit_wallet

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
# Create your tests here.
