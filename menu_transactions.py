from bank_account import BankAccount

class FrontEnd:
    # Handles accounts, balances, admin commands, and session transaction writing.

    def __init__(self):
        self.accounts = {}              # key: account_number (str) -> BankAccount
        self.current_user = None
        self.admin = False
        self.session_transactions = []  # buffer for current session transactions

    # ------------------------
    # ACCOUNT LOADING
    # ------------------------
    def load_accounts(self, filename: str):
        # Load accounts from fixed-width 37-char current_accounts.txt
        with open(filename, "r") as file:
            for line in file:
                line = line.rstrip("\n").ljust(37)
                name = line[5:25].strip()
                if name == "END_OF_FILE":
                    break
                acc_number = line[:5]
                status = line[25]
                balance_str = line[26:34].strip()
                try:
                    balance = float(balance_str)
                except ValueError:
                    balance = 0.0
                self.accounts[acc_number] = BankAccount(name, acc_number, balance, status)
    
    # ------------------------
    # LOGIN / LOGOUT
    # ------------------------
    def login(self, username, password=""):
        self.current_user = username
        self.admin = username.lower().startswith("admin")
        print(f"{username} logged in")

    def logout(self):
        if self.current_user:
            print(f"{self.current_user} logged out")
            self.write_session_file()
            self.current_user = None
            self.admin = False
        else:
            print("No user is currently logged in")
    
    # ------------------------
    # TRANSACTIONS
    # ------------------------
    def withdraw(self, acc_number, amount):
        if acc_number not in self.accounts:
            print(f"Account {acc_number} not found")
            return
        if not self.accounts[acc_number].is_active():
            print(f"Account {acc_number} is disabled, transaction denied")
            return
        account = self.accounts[acc_number]
        account.edit_balance(account.get_balance() - amount)
        print(f"Withdrew {amount} from {acc_number}")
        self.append_daily_transaction("01", account.account_name, acc_number, amount)

    def deposit(self, acc_number, amount):
        if acc_number not in self.accounts:
            print(f"Account {acc_number} not found")
            return
        if not self.accounts[acc_number].is_active():
            print(f"Account {acc_number} is disabled, transaction denied")
            return
        account = self.accounts[acc_number]
        account.edit_balance(account.get_balance() + amount)
        print(f"Deposited {amount} to {acc_number}")
        self.append_daily_transaction("04", account.account_name, acc_number, amount)

    def transfer(self, from_acc, to_acc, amount):
        if from_acc not in self.accounts or to_acc not in self.accounts:
            print("One or both accounts not found")
            return
        if not self.accounts[from_acc].is_active():
            print(f"Account {from_acc} is disabled, transaction denied")
            return
        if not self.accounts[to_acc].is_active():
            print(f"Account {to_acc} is disabled, transaction denied")
            return
        sender = self.accounts[from_acc]
        receiver = self.accounts[to_acc]
        sender.edit_balance(sender.get_balance() - amount)
        receiver.edit_balance(receiver.get_balance() + amount)
        print(f"Transferred {amount} from {from_acc} to {to_acc}")
        self.append_daily_transaction("02", sender.account_name, from_acc, amount)
        self.append_daily_transaction("02", receiver.account_name, to_acc, amount)

    def paybill(self, acc_number, payee, amount):
        if acc_number not in self.accounts:
            print(f"Account {acc_number} not found")
            return
        if not self.accounts[acc_number].is_active():
            print(f"Account {acc_number} is disabled, transaction denied")
            return
        account = self.accounts[acc_number]
        account.edit_balance(account.get_balance() - amount)
        print(f"{amount} paid to {payee} from {acc_number}")
        self.append_daily_transaction("03", account.account_name, acc_number, amount, payee)
    
    # ------------------------
    # ADMIN COMMANDS
    # ------------------------
    def create(self, acc_number, name, balance):
        if not self.admin:
            print("Only admin can create accounts")
            return
        self.accounts[acc_number] = BankAccount(name, acc_number, balance)
        print(f"Account {acc_number} created with balance {balance}")
        self.append_daily_transaction("05", name, acc_number, balance)

    def delete(self, acc_number):
        if not self.admin:
            print("Only admin can delete accounts")
            return
        if acc_number in self.accounts:
            name = self.accounts[acc_number].account_name
            del self.accounts[acc_number]
            print(f"Account {acc_number} deleted")
            self.append_daily_transaction("06", name, acc_number)
        else:
            print(f"Account {acc_number} not found")

    def disable(self, acc_number):
        if not self.admin:
            print("Only admin can disable accounts")
            return
        account = self.accounts[acc_number]
        account.status = "D"
        self.append_daily_transaction("07", account.account_name, acc_number)
        print(f"Account {acc_number} disabled")

    def changeplan(self, acc_number):
        if not self.admin:
            print("Only admin can change plans")
            return
        account = self.accounts[acc_number]
        account.payment_plan = "NP" # Switch from student plan to non-student
        print(f"Account {acc_number} changeplan to a non-student plan")
        self.append_daily_transaction("08", account.account_name, acc_number)
    
    # ------------------------
    # SESSION TRANSACTION FILE
    # ------------------------
    def append_daily_transaction(self, code, name, acc_number, amount=0, misc=""):
        # Add transaction to buffer (40-char fixed-width format).
        name_field = name[:20].ljust(20)
        acc_field = str(acc_number).zfill(5)
        amount_field = f"{amount:08.2f}"
        misc_field = misc[:5].ljust(5)
        code_field = code.ljust(2)
        line = code_field + name_field + acc_field + amount_field + misc_field
        self.session_transactions.append(line[:40])

    def write_session_file(self):
        # Write all session transactions to daily_transactions.txt with end-of-session line.
        with open("daily_transactions.txt", "a") as file:
            for t in self.session_transactions:
                file.write(t + "\n")
            end_line = "00" + " " * 20 + "00000" + "00000.00" + " " * 5
            file.write(end_line + "\n")
        self.session_transactions = []
