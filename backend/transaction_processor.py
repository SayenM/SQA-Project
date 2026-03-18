# transaction_processor.py
"""
Applies every transaction from the merged transaction file to the in-memory
account store, enforces business constraints, charges per-transaction fees,
and logs constraint violations to the terminal.

Transaction codes (matching the Front End):
    01 – Withdrawal
    02 – Transfer    (Front End writes TWO lines: first = debit, second = credit)
    03 – Paybill
    04 – Deposit
    05 – Create account
    06 – Delete account
    07 – Disable account
    08 – Change plan

Fee schedule (charged after every financial transaction):
    Student plan ('S')     : $0.05 per transaction
    Non-student plan ('N') : $0.10 per transaction

Constraint violations are printed in the format:
    CONSTRAINT ERROR: <type> – <description>
      Transaction: <dict>

Fatal errors (unknown code) print a message and exit immediately.
"""

import sys
from account_manager import AccountManager


# ---------------------------------------------------------------------------
# Transaction code constants
# ---------------------------------------------------------------------------
TX_WITHDRAWAL   = "01"
TX_TRANSFER     = "02"
TX_PAYBILL      = "03"
TX_DEPOSIT      = "04"
TX_CREATE       = "05"
TX_DELETE       = "06"
TX_DISABLE      = "07"
TX_CHANGE_PLAN  = "08"


class TransactionProcessor:
    """
    Dispatches each parsed transaction dict to the correct handler method.

    Constraint failures are logged and the failing transaction is skipped;
    all subsequent transactions continue to be processed normally.

    Attributes:
        _accounts (AccountManager): Live in-memory account store.
    """

    def __init__(self, account_manager: AccountManager):
        """
        Stores a reference to the AccountManager to be mutated during processing.

        Args:
            account_manager (AccountManager): The loaded account store.
        """
        self._accounts = account_manager

    # ------------------------------------------------------------------
    # Main dispatch loop
    # ------------------------------------------------------------------

    def process_all(self, transactions: list) -> None:
        """
        Iterates over every transaction dict and dispatches to the handler
        for that transaction code.

        Transfer transactions (code "02") are special: the Front End writes
        two consecutive lines for each transfer — the first for the debit
        account and the second for the credit account.  This method pairs
        them up before dispatching.

        Unknown transaction codes are treated as fatal errors.

        Args:
            transactions (list[dict]): From FileHandler.load_transactions().
        """
        i = 0
        while i < len(transactions):
            tx = transactions[i]
            code = tx['code']

            if code == TX_WITHDRAWAL:
                self._process_withdrawal(tx)
                i += 1

            elif code == TX_TRANSFER:
                # Pair the debit line (current) with the credit line (next)
                if i + 1 < len(transactions) and transactions[i + 1]['code'] == TX_TRANSFER:
                    self._process_transfer(tx, transactions[i + 1])
                    i += 2
                else:
                    # Unpaired transfer line — log and skip
                    self._log_constraint_error(
                        "Unpaired transfer",
                        "Transfer transaction has no matching second line.", tx)
                    i += 1

            elif code == TX_PAYBILL:
                self._process_paybill(tx)
                i += 1

            elif code == TX_DEPOSIT:
                self._process_deposit(tx)
                i += 1

            elif code == TX_CREATE:
                self._process_create(tx)
                i += 1

            elif code == TX_DELETE:
                self._process_delete(tx)
                i += 1

            elif code == TX_DISABLE:
                self._process_disable(tx)
                i += 1

            elif code == TX_CHANGE_PLAN:
                self._process_change_plan(tx)
                i += 1

            else:
                print(f"FATAL ERROR: Unknown transaction code '{code}' "
                      f"in transaction: {tx}. Aborting.")
                sys.exit(1)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _charge_fee(self, account) -> bool:
        """
        Debits the per-transaction fee from the account and increments
        its transaction count.

        Logs a constraint error (but does NOT skip the parent transaction)
        if the fee itself would cause a negative balance — the fee is then
        not applied.

        Args:
            account (Account): Account to debit the fee from.

        Returns:
            bool: True if the fee was applied, False if it was skipped.
        """
        fee = account.transaction_fee()
        if round(account.balance - fee, 2) < 0.00:
            self._log_constraint_error(
                "Negative balance after fee",
                f"Account {account.number} balance ${account.balance:.2f} cannot "
                f"cover the ${fee:.2f} transaction fee; fee waived."
            )
            # Still count the transaction even if fee cannot be charged
            account.transaction_count += 1
            return False

        account.balance           = round(account.balance - fee, 2)
        account.transaction_count += 1
        return True

    @staticmethod
    def _log_constraint_error(error_type: str, description: str,
                              transaction: dict = None) -> None:
        """
        Prints a formatted constraint violation to the terminal.

        Args:
            error_type  (str) : Short category label.
            description (str) : Human-readable explanation.
            transaction (dict): The offending transaction (optional).
        """
        print(f"CONSTRAINT ERROR: {error_type} – {description}")
        if transaction is not None:
            print(f"  Transaction: {transaction}")

    # ------------------------------------------------------------------
    # Transaction handlers
    # ------------------------------------------------------------------

    def _process_withdrawal(self, tx: dict) -> None:
        """
        Handles code 01 – Withdrawal.

        Subtracts the amount from the account balance, then charges the fee.
        Constraints: account must exist, be active, and have sufficient funds.

        Args:
            tx (dict): Transaction dict with 'number' and 'amount'.
        """
        account = self._accounts.find(tx['number'])

        if account is None:
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} for withdrawal.", tx)
            return

        if not account.is_active():
            self._log_constraint_error(
                "Account disabled",
                f"Account {account.number} is disabled; withdrawal refused.", tx)
            return

        new_balance = round(account.balance - tx['amount'], 2)
        if new_balance < 0.00:
            self._log_constraint_error(
                "Negative balance",
                f"Withdrawing ${tx['amount']:.2f} from account {account.number} "
                f"(balance ${account.balance:.2f}) would cause a negative balance.", tx)
            return

        account.balance = new_balance
        self._charge_fee(account)

    def _process_transfer(self, debit_tx: dict, credit_tx: dict) -> None:
        """
        Handles code 02 – Transfer.

        The Front End writes two consecutive "02" lines per transfer:
          debit_tx  = the account being debited (money leaves)
          credit_tx = the account being credited (money arrives)

        Constraints: both accounts must exist and be active; debit account
        must have sufficient funds.  Fee is charged to the debit account only.

        Args:
            debit_tx  (dict): First  "02" transaction line (source account).
            credit_tx (dict): Second "02" transaction line (destination account).
        """
        from_account = self._accounts.find(debit_tx['number'])
        to_account   = self._accounts.find(credit_tx['number'])

        if from_account is None:
            self._log_constraint_error(
                "Source account not found",
                f"No account {debit_tx['number']} for transfer debit.", debit_tx)
            return

        if to_account is None:
            self._log_constraint_error(
                "Destination account not found",
                f"No account {credit_tx['number']} for transfer credit.", credit_tx)
            return

        if not from_account.is_active():
            self._log_constraint_error(
                "Source account disabled",
                f"Account {from_account.number} is disabled.", debit_tx)
            return

        if not to_account.is_active():
            self._log_constraint_error(
                "Destination account disabled",
                f"Account {to_account.number} is disabled.", credit_tx)
            return

        amount = debit_tx['amount']
        new_from_balance = round(from_account.balance - amount, 2)
        if new_from_balance < 0.00:
            self._log_constraint_error(
                "Negative balance",
                f"Transferring ${amount:.2f} from account {from_account.number} "
                f"(balance ${from_account.balance:.2f}) would cause a negative balance.",
                debit_tx)
            return

        from_account.balance = new_from_balance
        to_account.balance   = round(to_account.balance + amount, 2)
        self._charge_fee(from_account)   # Fee only on the sending account

    def _process_paybill(self, tx: dict) -> None:
        """
        Handles code 03 – Paybill.

        Subtracts the amount from the account and charges the fee.
        Constraints: account must exist, be active, and have sufficient funds.

        Args:
            tx (dict): Transaction dict with 'number', 'amount', and 'misc' (payee).
        """
        account = self._accounts.find(tx['number'])

        if account is None:
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} for paybill.", tx)
            return

        if not account.is_active():
            self._log_constraint_error(
                "Account disabled",
                f"Account {account.number} is disabled; paybill refused.", tx)
            return

        new_balance = round(account.balance - tx['amount'], 2)
        if new_balance < 0.00:
            self._log_constraint_error(
                "Negative balance",
                f"Paybill of ${tx['amount']:.2f} from account {account.number} "
                f"(balance ${account.balance:.2f}) would cause a negative balance.", tx)
            return

        account.balance = new_balance
        self._charge_fee(account)

    def _process_deposit(self, tx: dict) -> None:
        """
        Handles code 04 – Deposit.

        Adds the amount to the account balance, then charges the fee.
        Constraints: account must exist and be active.

        Args:
            tx (dict): Transaction dict with 'number' and 'amount'.
        """
        account = self._accounts.find(tx['number'])

        if account is None:
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} for deposit.", tx)
            return

        if not account.is_active():
            self._log_constraint_error(
                "Account disabled",
                f"Account {account.number} is disabled; deposit refused.", tx)
            return

        account.balance = round(account.balance + tx['amount'], 2)
        self._charge_fee(account)

    def _process_create(self, tx: dict) -> None:
        """
        Handles code 05 – Create Account.

        Creates a new active account with a $0.00 balance.
        Constraint: account number must not already exist.

        The Front End does not include a plan code in the create transaction,
        so new accounts default to student plan ('S').

        Args:
            tx (dict): Transaction dict with 'number' and 'name'.
        """
        if self._accounts.exists(tx['number']):
            self._log_constraint_error(
                "Duplicate account number",
                f"Account {tx['number']} already exists; create refused.", tx)
            return

        self._accounts.create(
            number = tx['number'],
            name   = tx['name'],
            plan   = 'S',    # Front End does not transmit a plan; default to student
        )

    def _process_delete(self, tx: dict) -> None:
        """
        Handles code 06 – Delete Account.

        Removes the account from the store.
        Constraint: account must exist.

        Args:
            tx (dict): Transaction dict with 'number'.
        """
        if not self._accounts.exists(tx['number']):
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} to delete.", tx)
            return

        self._accounts.delete(tx['number'])

    def _process_disable(self, tx: dict) -> None:
        """
        Handles code 07 – Disable Account.

        Sets the account status to 'D' (disabled).
        Constraint: account must exist.

        Args:
            tx (dict): Transaction dict with 'number'.
        """
        account = self._accounts.find(tx['number'])

        if account is None:
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} to disable.", tx)
            return

        account.status = 'D'

    def _process_change_plan(self, tx: dict) -> None:
        """
        Handles code 08 – Change Plan.

        The Front End always sets payment_plan to "NP" on changeplan,
        so the Back End mirrors this: any changeplan transaction sets
        the account to non-student plan ('N').

        Constraint: account must exist.

        Args:
            tx (dict): Transaction dict with 'number'.
        """
        account = self._accounts.find(tx['number'])

        if account is None:
            self._log_constraint_error(
                "Account not found",
                f"No account {tx['number']} for changeplan.", tx)
            return

        # Front End sets plan to "NP" unconditionally; Back End mirrors that behaviour
        account.plan = 'N'