# bank_account.py
"""
Defines the BankAccount class, which represents a user's bank account with attributes like name, number, balance, status, and payment plan.
"""
class BankAccount:
    # Represents a user bank account.

    def __init__(self, acc_name: str, acc_number: str, balance: float, status="A", payment_plan="SP"):
        self.account_name = acc_name
        self.account_number = acc_number
        self.balance = float(balance)
        self.status = status # A for active, D for disabled
        self.payment_plan = payment_plan # SP for student plan, NP for non-student plan

    def get_balance(self) -> float:
        # Returns the current account balance.
        return self.balance

    def edit_balance(self, new_balance: float):
        # Updates the account balance.
        self.balance = float(new_balance)

    def is_active(self):
        # Returns the account status (active or disabled).
        return self.status == "A"