# account_manager.py
"""
In-memory store for all bank accounts loaded from the Current Accounts File.

Provides lookup, creation, and deletion helpers that TransactionProcessor
calls while applying transactions.  Deliberately holds no business logic
(no fee charging, no constraint checking) — those belong to TransactionProcessor.
"""

from account import Account


class AccountManager:
    """
    Dictionary-backed store mapping account number (str) to Account objects.

    After all transactions are processed, get_all_accounts() returns the
    full updated list for FileHandler to write to the output files.

    Attributes:
        _accounts (dict): { account_number_str : Account }
    """

    def __init__(self, accounts: list):
        """
        Builds the internal dictionary from a list of Account objects.

        Args:
            accounts (list[Account]): Loaded by FileHandler.load_current_accounts().
        """
        self._accounts = {account.number: account for account in accounts}

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def find(self, number: str):
        """
        Returns the Account with the given number, or None if not found.

        Args:
            number (str): 5-digit account number string.

        Returns:
            Account | None
        """
        return self._accounts.get(number)

    def exists(self, number: str) -> bool:
        """
        Returns True if an account with the given number is in the store.

        Args:
            number (str): Account number to check.

        Returns:
            bool
        """
        return number in self._accounts

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def create(self, number: str, name: str, plan: str = 'S') -> Account:
        """
        Creates a new active Account with a $0.00 balance and inserts it.

        Args:
            number (str): Unique 5-digit account number for the new account.
            name   (str): Account holder name (spaces, not underscores).
            plan   (str): 'S' (student) or 'N' (non-student); defaults to 'S'.

        Returns:
            Account: The newly created Account.
        """
        new_account = Account(
            number            = number,
            name              = name,
            status            = 'A',    # New accounts are always active
            balance           = 0.00,
            transaction_count = 0,
            plan              = plan,
        )
        self._accounts[number] = new_account
        return new_account

    def delete(self, number: str) -> bool:
        """
        Removes the account with the given number from the store.

        Args:
            number (str): Account number to remove.

        Returns:
            bool: True if the account existed and was removed, False otherwise.
        """
        if number in self._accounts:
            del self._accounts[number]
            return True
        return False

    # ------------------------------------------------------------------
    # Bulk retrieval (for writing output files)
    # ------------------------------------------------------------------

    def get_all_accounts(self) -> list:
        """
        Returns all Account objects in the store as an unsorted list.

        FileHandler is responsible for sorting before writing.

        Returns:
            list[Account]
        """
        return list(self._accounts.values())