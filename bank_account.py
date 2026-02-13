# bank_account.py

class BankAccount:
    """Represents a user bank account."""

    def __init__(self, acc_name: str, acc_number: str, balance: float):
        self.account_name = acc_name
        self.account_number = acc_number
        self.balance = float(balance)
        self.status = "A" # A for active, I for inactive

    def get_balance(self) -> float:
        """Returns the current account balance."""
        return self.balance

    def edit_balance(self, new_balance: float):
        """Updates the account balance."""
        self.balance = float(new_balance)
