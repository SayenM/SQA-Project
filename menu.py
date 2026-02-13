# menu.py
"""
Front End Prototype for Phase #2 with admin commands

Reads:
- current_accounts.txt
- available_units.txt

Takes transactions from standard input.
Outputs responses on standard output.
Writes transactions to daily_transactions.txt.
"""

from models import BankAccount

class FrontEnd:
    """Handles transaction processing and file interaction including login/logout and admin commands."""

    def __init__(self):
        self.accounts = {}
        self.units = {}
        self.current_user = None
        self.admin = False

    def load_accounts(self, filename: str):
        """Loads current accounts from file."""
        with open(filename, "r") as file:
            for line in file:
                acc_number, name, balance = line.strip().split()
                self.accounts[acc_number] = BankAccount(name, acc_number, float(balance))

    def load_units(self, filename: str):
        """Loads available rental units from file."""
        with open(filename, "r") as file:
            for line in file:
                unit_id, price, status = line.strip().split()
                self.units[unit_id] = {"price": price, "status": status}

    def append_daily_transaction(self, command: str):
        """Appends a transaction or login/logout command to daily_transactions.txt."""
        with open("daily_transactions.txt", "a") as file:
            file.write(command + "\n")

    def process_transaction(self, command: str):
        """Processes a single transaction command including login/logout and admin commands."""
        parts = command.strip().split()
        if not parts:
            return

        action = parts[0].upper()

        # LOGIN / LOGOUT
        if action == "LOGIN":
            username = parts[1]
            password = parts[2] if len(parts) > 2 else ""
            self.current_user = username
            self.admin = username.lower().startswith("admin")
            print(f"{username} logged in")
            self.append_daily_transaction(command)

        elif action == "LOGOUT":
            if self.current_user:
                print(f"{self.current_user} logged out")
                self.current_user = None
                self.admin = False
                self.append_daily_transaction(command)
            else:
                print("No user is currently logged in")

        # TRANSACTIONS
        elif action == "WITHDRAW":
            acc, amount = parts[1], float(parts[2])
            if acc not in self.accounts:
                print(f"Account {acc} not found")
                return
            self.accounts[acc].edit_balance(self.accounts[acc].get_balance() - amount)
            print(f"Withdrew {amount} from {acc}")
            self.append_daily_transaction(command)

        elif action == "DEPOSIT":
            acc, amount = parts[1], float(parts[2])
            if acc not in self.accounts:
                print(f"Account {acc} not found")
                return
            self.accounts[acc].edit_balance(self.accounts[acc].get_balance() + amount)
            print(f"Deposited {amount} to {acc}")
            self.append_daily_transaction(command)

        elif action == "TRANSFER":
            acc1, acc2, amount = parts[1], parts[2], float(parts[3])
            if acc1 not in self.accounts or acc2 not in self.accounts:
                print(f"One or both accounts not found")
                return
            self.accounts[acc1].edit_balance(self.accounts[acc1].get_balance() - amount)
            self.accounts[acc2].edit_balance(self.accounts[acc2].get_balance() + amount)
            print(f"Transferred {amount} from {acc1} to {acc2}")
            self.append_daily_transaction(command)

        elif action == "PAYBILL":
            acc, payee, amount = parts[1], parts[2], float(parts[3])
            if acc not in self.accounts:
                print(f"Account {acc} not found")
                return
            self.accounts[acc].edit_balance(self.accounts[acc].get_balance() - amount)
            print(f"{amount} paid to {payee} from {acc}")
            self.append_daily_transaction(command)

        # ADMIN COMMANDS
        elif action == "CREATE":
            if not self.admin:
                print("Only admin can create accounts")
                return
            acc_number = parts[1]
            name = parts[2]
            balance = float(parts[3])
            self.accounts[acc_number] = BankAccount(name, acc_number, balance)
            print(f"Account {acc_number} created with balance {balance}")
            self.append_daily_transaction(command)

        elif action == "DELETE":
            if not self.admin:
                print("Only admin can delete accounts")
                return
            acc_number = parts[1]
            if acc_number in self.accounts:
                del self.accounts[acc_number]
                print(f"Account {acc_number} deleted")
            else:
                print(f"Account {acc_number} not found")
            self.append_daily_transaction(command)

        elif action == "DISABLE":
            if not self.admin:
                print("Only admin can disable accounts")
                return
            # Placeholder: actual disable logic not implemented
            acc_number = parts[1]
            print(f"Account {acc_number} disable not implemented yet")
            self.append_daily_transaction(command)

        elif action == "CHANGEPLAN":
            if not self.admin:
                print("Only admin can change plans")
                return
            # Placeholder: actual plan change not implemented
            acc_number = parts[1]
            print(f"Account {acc_number} changeplan not implemented yet")
            self.append_daily_transaction(command)

def main():
    frontend = FrontEnd()
    frontend.load_accounts("current_accounts.txt")
    frontend.load_units("available_units.txt")

    while True:
        try:
            command = input()
            frontend.process_transaction(command)
        except EOFError:
            break

if __name__ == "__main__":
    main()
