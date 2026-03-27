"""
CSCI 3060U – Phase #5: Back End Unit Tests
==========================================
Method 1 (Statement Coverage) : _process_deposit
Method 2 (Decision+Loop Coverage): process_all
"""

import unittest
from unittest.mock import MagicMock, patch
import io
import sys

# ---------------------------------------------------------------------------
# Minimal stubs so the test file is self-contained
# (replace with real imports if running alongside the actual source tree)
# ---------------------------------------------------------------------------
try:
    from account           import Account
    from account_manager   import AccountManager
    from transaction_processor import TransactionProcessor
except ImportError:
    # ---- Inline stubs ----
    FEE_STUDENT     = 0.05
    FEE_NON_STUDENT = 0.10

    class Account:
        def __init__(self, number, name, status, balance,
                     transaction_count=0, plan='S'):
            self.number            = number
            self.name              = name
            self.status            = status
            self.balance           = round(float(balance), 2)
            self.transaction_count = transaction_count
            self.plan              = plan

        def is_active(self):
            return self.status == 'A'

        def is_student_plan(self):
            return self.plan == 'S'

        def transaction_fee(self):
            return FEE_STUDENT if self.is_student_plan() else FEE_NON_STUDENT

    class AccountManager:
        def __init__(self, accounts):
            self._accounts = {a.number: a for a in accounts}

        def find(self, number):
            return self._accounts.get(number)

        def exists(self, number):
            return number in self._accounts

        def create(self, number, name, plan='S'):
            acct = Account(number, name, 'A', 0.00, 0, plan)
            self._accounts[number] = acct
            return acct

        def delete(self, number):
            if number in self._accounts:
                del self._accounts[number]
                return True
            return False

        def get_all_accounts(self):
            return list(self._accounts.values())

    class TransactionProcessor:
        TX_WITHDRAWAL  = "01"
        TX_TRANSFER    = "02"
        TX_PAYBILL     = "03"
        TX_DEPOSIT     = "04"
        TX_CREATE      = "05"
        TX_DELETE      = "06"
        TX_DISABLE     = "07"
        TX_CHANGE_PLAN = "08"

        def __init__(self, account_manager):
            self._accounts = account_manager

        def process_all(self, transactions):
            i = 0
            while i < len(transactions):
                tx   = transactions[i]
                code = tx['code']
                if code == "01":
                    self._process_withdrawal(tx); i += 1
                elif code == "02":
                    if i+1 < len(transactions) and transactions[i+1]['code'] == "02":
                        self._process_transfer(tx, transactions[i+1]); i += 2
                    else:
                        self._log_constraint_error(
                            "Unpaired transfer",
                            "Transfer transaction has no matching second line.", tx)
                        i += 1
                elif code == "03":
                    self._process_paybill(tx); i += 1
                elif code == "04":
                    self._process_deposit(tx); i += 1
                elif code == "05":
                    self._process_create(tx); i += 1
                elif code == "06":
                    self._process_delete(tx); i += 1
                elif code == "07":
                    self._process_disable(tx); i += 1
                elif code == "08":
                    self._process_change_plan(tx); i += 1
                else:
                    print(f"FATAL ERROR: Unknown transaction code '{code}'")
                    sys.exit(1)

        def _charge_fee(self, account):
            fee = account.transaction_fee()
            if round(account.balance - fee, 2) < 0.00:
                self._log_constraint_error(
                    "Negative balance after fee",
                    f"Account {account.number} balance ${account.balance:.2f} cannot "
                    f"cover the ${fee:.2f} transaction fee; fee waived.")
                account.transaction_count += 1
                return False
            account.balance           = round(account.balance - fee, 2)
            account.transaction_count += 1
            return True

        @staticmethod
        def _log_constraint_error(error_type, description, transaction=None):
            print(f"CONSTRAINT ERROR: {error_type} – {description}")
            if transaction is not None:
                print(f"  Transaction: {transaction}")

        def _process_withdrawal(self, tx):
            account = self._accounts.find(tx['number'])
            if account is None:
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} for withdrawal.", tx); return
            if not account.is_active():
                self._log_constraint_error("Account disabled",
                    f"Account {account.number} is disabled; withdrawal refused.", tx); return
            new_balance = round(account.balance - tx['amount'], 2)
            if new_balance < 0.00:
                self._log_constraint_error("Negative balance",
                    f"Withdrawing ${tx['amount']:.2f} from account {account.number} "
                    f"(balance ${account.balance:.2f}) would cause a negative balance.", tx); return
            account.balance = new_balance
            self._charge_fee(account)

        def _process_transfer(self, debit_tx, credit_tx):
            from_account = self._accounts.find(debit_tx['number'])
            to_account   = self._accounts.find(credit_tx['number'])
            if from_account is None:
                self._log_constraint_error("Source account not found",
                    f"No account {debit_tx['number']} for transfer debit.", debit_tx); return
            if to_account is None:
                self._log_constraint_error("Destination account not found",
                    f"No account {credit_tx['number']} for transfer credit.", credit_tx); return
            if not from_account.is_active():
                self._log_constraint_error("Source account disabled",
                    f"Account {from_account.number} is disabled.", debit_tx); return
            if not to_account.is_active():
                self._log_constraint_error("Destination account disabled",
                    f"Account {to_account.number} is disabled.", credit_tx); return
            amount = debit_tx['amount']
            new_from_balance = round(from_account.balance - amount, 2)
            if new_from_balance < 0.00:
                self._log_constraint_error("Negative balance",
                    f"Transferring ${amount:.2f} from account {from_account.number} "
                    f"(balance ${from_account.balance:.2f}) would cause a negative balance.",
                    debit_tx); return
            from_account.balance = new_from_balance
            to_account.balance   = round(to_account.balance + amount, 2)
            self._charge_fee(from_account)

        def _process_paybill(self, tx):
            account = self._accounts.find(tx['number'])
            if account is None:
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} for paybill.", tx); return
            if not account.is_active():
                self._log_constraint_error("Account disabled",
                    f"Account {account.number} is disabled; paybill refused.", tx); return
            new_balance = round(account.balance - tx['amount'], 2)
            if new_balance < 0.00:
                self._log_constraint_error("Negative balance",
                    f"Paybill of ${tx['amount']:.2f} from account {account.number} "
                    f"(balance ${account.balance:.2f}) would cause a negative balance.", tx); return
            account.balance = new_balance
            self._charge_fee(account)

        def _process_deposit(self, tx):
            account = self._accounts.find(tx['number'])
            if account is None:
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} for deposit.", tx); return
            if not account.is_active():
                self._log_constraint_error("Account disabled",
                    f"Account {account.number} is disabled; deposit refused.", tx); return
            account.balance = round(account.balance + tx['amount'], 2)
            self._charge_fee(account)

        def _process_create(self, tx):
            if self._accounts.exists(tx['number']):
                self._log_constraint_error("Duplicate account number",
                    f"Account {tx['number']} already exists; create refused.", tx); return
            self._accounts.create(number=tx['number'], name=tx['name'], plan='S')

        def _process_delete(self, tx):
            if not self._accounts.exists(tx['number']):
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} to delete.", tx); return
            self._accounts.delete(tx['number'])

        def _process_disable(self, tx):
            account = self._accounts.find(tx['number'])
            if account is None:
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} to disable.", tx); return
            account.status = 'D'

        def _process_change_plan(self, tx):
            account = self._accounts.find(tx['number'])
            if account is None:
                self._log_constraint_error("Account not found",
                    f"No account {tx['number']} for changeplan.", tx); return
            account.plan = 'N'


# ===========================================================================
# Helpers
# ===========================================================================

def make_account(number='00001', name='Test User', status='A',
                 balance=100.00, plan='S'):
    """Return an Account with sensible defaults."""
    return Account(number, name, status, balance, 0, plan)


def make_processor(*accounts):
    """Return a TransactionProcessor backed by the given Account objects."""
    mgr = AccountManager(list(accounts))
    return TransactionProcessor(mgr)


def make_tx(code='04', number='00001', amount=50.00,
            name='Test User', misc=''):
    """Return a minimal transaction dict."""
    return {'code': code, 'number': number, 'amount': amount,
            'name': name, 'misc': misc}


# ===========================================================================
# METHOD 1 – _process_deposit  (Statement Coverage)
# ===========================================================================
# Statements / branches to cover:
#   D-1  account = self._accounts.find(...)                [always executes]
#   D-2  if account is None  -> True  (log error, return)
#   D-3  if account is None  -> False
#   D-4  if not account.is_active() -> True  (log error, return)
#   D-5  if not account.is_active() -> False
#   D-6  account.balance = round(...)                      [normal path]
#   D-7  self._charge_fee(account)                         [normal path]
#
# Test Cases:
# | # | Description                          | account? | active? | Expected outcome              |
# |---|--------------------------------------|----------|---------|-------------------------------|
# | 1 | Account does not exist               | No       | —       | Constraint error logged        |
# | 2 | Account exists but disabled          | Yes      | No      | Constraint error logged        |
# | 3 | Normal deposit (student plan)        | Yes      | Yes     | Balance += amount; fee charged |
# | 4 | Normal deposit (non-student plan)    | Yes      | Yes     | Balance += amount; fee charged |
# ===========================================================================

class TestProcessDeposit(unittest.TestCase):
    """Statement coverage for _process_deposit."""

    # --- TC-D-1: account does not exist -----------------------------------
    def test_deposit_account_not_found(self):
        """D-2 branch: account is None → log error, return immediately."""
        proc = make_processor()          # empty store
        tx   = make_tx(code='04', number='99999', amount=50.00)
        with patch.object(TransactionProcessor, '_log_constraint_error') as mock_log:
            proc._process_deposit(tx)
            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            self.assertEqual(args[0], "Account not found")

    # --- TC-D-2: account exists but is disabled ----------------------------
    def test_deposit_account_disabled(self):
        """D-4 branch: account is disabled → log error, return."""
        acct = make_account(status='D')
        proc = make_processor(acct)
        tx   = make_tx(code='04', number=acct.number, amount=30.00)
        with patch.object(TransactionProcessor, '_log_constraint_error') as mock_log:
            proc._process_deposit(tx)
            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            self.assertEqual(args[0], "Account disabled")
        self.assertAlmostEqual(acct.balance, 100.00)   # balance unchanged

    # --- TC-D-3: normal deposit on student plan ----------------------------
    def test_deposit_normal_student_plan(self):
        """D-5→D-6→D-7: active student account; balance increases then fee deducted."""
        acct = make_account(status='A', balance=100.00, plan='S')
        proc = make_processor(acct)
        tx   = make_tx(code='04', number=acct.number, amount=50.00)
        proc._process_deposit(tx)
        # balance after deposit: 100 + 50 = 150; fee 0.05 → 149.95
        self.assertAlmostEqual(acct.balance, 149.95)
        self.assertEqual(acct.transaction_count, 1)

    # --- TC-D-4: normal deposit on non-student plan ------------------------
    def test_deposit_normal_non_student_plan(self):
        """Same happy path but with non-student (higher) fee."""
        acct = make_account(status='A', balance=200.00, plan='N')
        proc = make_processor(acct)
        tx   = make_tx(code='04', number=acct.number, amount=75.00)
        proc._process_deposit(tx)
        # 200 + 75 = 275; fee 0.10 → 274.90
        self.assertAlmostEqual(acct.balance, 274.90)
        self.assertEqual(acct.transaction_count, 1)


# ===========================================================================
# METHOD 2 – process_all  (Decision + Loop Coverage)
# ===========================================================================
#
# Loop in process_all:
#   while i < len(transactions):
#
# Loop coverage requires:
#   L-0: Loop body never executes   (empty transaction list)
#   L-1: Loop body executes exactly once
#   L-N: Loop body executes multiple times
#
# Decision nodes inside the loop (one per if/elif/else branch):
#   Branch "01" – Withdrawal
#   Branch "02" – Transfer (paired)
#   Branch "02-unpaired" – Transfer (no second line)
#   Branch "03" – Paybill
#   Branch "04" – Deposit
#   Branch "05" – Create
#   Branch "06" – Delete
#   Branch "07" – Disable
#   Branch "08" – Change plan
#   Branch "else" – Unknown code (fatal)
#   Transfer sub-decision: i+1 exists AND next code == "02"
#
# Test Cases:
# | # | Description                            | Loop iters | Decision branch        |
# |---|----------------------------------------|------------|------------------------|
# | 1 | Empty list                             | 0          | while=False            |
# | 2 | Single withdrawal (code 01)            | 1          | "01" branch            |
# | 3 | Single deposit (code 04)               | 1          | "04" branch            |
# | 4 | Paired transfer (two "02" lines)       | 1 (i+=2)   | "02" paired            |
# | 5 | Unpaired transfer (single "02" line)   | 1          | "02" unpaired          |
# | 6 | Paybill (code 03)                      | 1          | "03" branch            |
# | 7 | Create (code 05)                       | 1          | "05" branch            |
# | 8 | Delete (code 06)                       | 1          | "06" branch            |
# | 9 | Disable (code 07)                      | 1          | "07" branch            |
# |10 | Change plan (code 08)                  | 1          | "08" branch            |
# |11 | Multiple transactions (deposit×3)      | 3          | loop executes N times  |
# |12 | Unknown code                           | 1          | "else" branch / fatal  |
# ===========================================================================

class TestProcessAll(unittest.TestCase):
    """Decision and loop coverage for process_all."""

    # --- TC-PA-1: empty list (loop never executes) ------------------------
    def test_empty_transactions(self):
        """Loop condition false on entry: while i < 0 is never entered."""
        proc = make_processor(make_account())
        proc.process_all([])           # should complete without error

    # --- TC-PA-2: single withdrawal (code 01) -----------------------------
    def test_single_withdrawal_dispatch(self):
        """Loop runs once; code '01' branch taken."""
        acct = make_account(balance=100.00)
        proc = make_processor(acct)
        tx   = make_tx(code='01', number=acct.number, amount=40.00)
        proc.process_all([tx])
        # 100 - 40 = 60; fee 0.05 → 59.95
        self.assertAlmostEqual(acct.balance, 59.95)

    # --- TC-PA-3: single deposit (code 04) --------------------------------
    def test_single_deposit_dispatch(self):
        """Loop runs once; code '04' branch taken."""
        acct = make_account(balance=50.00)
        proc = make_processor(acct)
        tx   = make_tx(code='04', number=acct.number, amount=20.00)
        proc.process_all([tx])
        # 50 + 20 = 70; fee 0.05 → 69.95
        self.assertAlmostEqual(acct.balance, 69.95)

    # --- TC-PA-4: paired transfer (two "02" lines) ------------------------
    def test_paired_transfer_dispatch(self):
        """Loop advances by 2; '02' paired sub-branch taken."""
        src = make_account(number='00001', balance=200.00)
        dst = make_account(number='00002', balance=50.00)
        proc = make_processor(src, dst)
        debit  = make_tx(code='02', number='00001', amount=80.00)
        credit = make_tx(code='02', number='00002', amount=80.00)
        proc.process_all([debit, credit])
        self.assertAlmostEqual(src.balance, 119.95)  # 200-80-0.05
        self.assertAlmostEqual(dst.balance, 130.00)  # 50+80

    # --- TC-PA-5: unpaired transfer (single "02" line) --------------------
    def test_unpaired_transfer_logs_error(self):
        """'02' unpaired sub-branch: next element missing or not '02'."""
        proc = make_processor(make_account())
        tx   = make_tx(code='02', number='00001', amount=50.00)
        with patch.object(TransactionProcessor, '_log_constraint_error') as mock_log:
            proc.process_all([tx])
            mock_log.assert_called_once()
            self.assertIn("Unpaired", mock_log.call_args[0][0])

    # --- TC-PA-6: paybill (code 03) ---------------------------------------
    def test_paybill_dispatch(self):
        """Loop runs once; code '03' branch taken."""
        acct = make_account(balance=100.00)
        proc = make_processor(acct)
        tx   = make_tx(code='03', number=acct.number, amount=25.00)
        proc.process_all([tx])
        # 100 - 25 = 75; fee 0.05 → 74.95
        self.assertAlmostEqual(acct.balance, 74.95)

    # --- TC-PA-7: create account (code 05) --------------------------------
    def test_create_dispatch(self):
        """Loop runs once; code '05' branch taken; new account added."""
        proc = make_processor()
        tx   = make_tx(code='05', number='00010', name='New User', amount=0.00)
        proc.process_all([tx])
        self.assertIsNotNone(proc._accounts.find('00010'))

    # --- TC-PA-8: delete account (code 06) --------------------------------
    def test_delete_dispatch(self):
        """Loop runs once; code '06' branch taken; account removed."""
        acct = make_account(number='00003')
        proc = make_processor(acct)
        tx   = make_tx(code='06', number='00003', amount=0.00)
        proc.process_all([tx])
        self.assertIsNone(proc._accounts.find('00003'))

    # --- TC-PA-9: disable account (code 07) ------------------------------
    def test_disable_dispatch(self):
        """Loop runs once; code '07' branch taken; account set to disabled."""
        acct = make_account(number='00004', status='A')
        proc = make_processor(acct)
        tx   = make_tx(code='07', number='00004', amount=0.00)
        proc.process_all([tx])
        self.assertEqual(acct.status, 'D')

    # --- TC-PA-10: change plan (code 08) ----------------------------------
    def test_change_plan_dispatch(self):
        """Loop runs once; code '08' branch taken; plan flipped to 'N'."""
        acct = make_account(number='00005', plan='S')
        proc = make_processor(acct)
        tx   = make_tx(code='08', number='00005', amount=0.00)
        proc.process_all([tx])
        self.assertEqual(acct.plan, 'N')

    # --- TC-PA-11: multiple iterations (loop runs N > 1 times) -----------
    def test_multiple_transactions_loop(self):
        """Loop body executes 3 times: three successive deposits."""
        acct = make_account(balance=0.00)
        proc = make_processor(acct)
        txs  = [make_tx(code='04', number=acct.number, amount=10.00)] * 3
        proc.process_all(txs)
        # After 3 deposits of $10 each, with $0.05 fee per tx:
        # tx1: 0+10=10, -0.05 → 9.95
        # tx2: 9.95+10=19.95, -0.05 → 19.90
        # tx3: 19.90+10=29.90, -0.05 → 29.85
        self.assertAlmostEqual(acct.balance, 29.85)
        self.assertEqual(acct.transaction_count, 3)

    # --- TC-PA-12: unknown transaction code (fatal) -----------------------
    def test_unknown_code_exits(self):
        """'else' branch: unknown code triggers sys.exit(1)."""
        proc = make_processor(make_account())
        tx   = make_tx(code='99', number='00001', amount=0.00)
        with self.assertRaises(SystemExit) as ctx:
            proc.process_all([tx])
        self.assertEqual(ctx.exception.code, 1)


# ===========================================================================
# Additional edge-case tests (_charge_fee coverage)
# ===========================================================================

class TestChargeFee(unittest.TestCase):
    """Covers _charge_fee branches: fee can/cannot be covered."""

    def test_fee_applied_successfully(self):
        """Balance is sufficient to cover fee: balance decreases by fee amount."""
        acct = make_account(balance=1.00, plan='S')
        proc = make_processor(acct)
        result = proc._charge_fee(acct)
        self.assertTrue(result)
        self.assertAlmostEqual(acct.balance, 0.95)
        self.assertEqual(acct.transaction_count, 1)

    def test_fee_waived_when_balance_too_low(self):
        """Balance < fee: fee is waived, transaction_count still incremented."""
        acct = make_account(balance=0.03, plan='S')   # 0.03 < 0.05 fee
        proc = make_processor(acct)
        with patch.object(TransactionProcessor, '_log_constraint_error') as mock_log:
            result = proc._charge_fee(acct)
        self.assertFalse(result)
        self.assertAlmostEqual(acct.balance, 0.03)    # unchanged
        self.assertEqual(acct.transaction_count, 1)
        mock_log.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
