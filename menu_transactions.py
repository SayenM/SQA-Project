from bank_account import BankAccount
"""
Handles accounts, balances, admin commands, and session transaction writing.
"""

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

    # Login a user.
    # login
    # standard or admin
    # name (if standard)
    def login(self, session_type, name=""):
        if self.current_user:
            print("Error: Already logged in.")
            return
        self.current_user = session_type
        self.admin = (session_type == "admin")
        

    # Logout current user and write session transactions to file.
    # logout
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

    # withdrawal
    # account_number if in admin
    # amount
    def withdraw(self, acc_number, amount):
        if not self.current_user:
            print("Error: Not logged in.")
            return

        if acc_number not in self.accounts:
            print("Error: Invalid account.")
            return

        account = self.accounts[acc_number]

        if account.status != "A":
            print("Error: Account disabled.")
            return

        # standard mode limit
        if not self.admin and amount > 500.00:
            print("Error: Maximum withdrawal is $500.00.")
            return

        new_balance = account.get_balance() - amount
        if new_balance < 0:
            print("Error: Insufficient funds.")
            return

        account.edit_balance(new_balance)
        print(f"Withdrawal of ${amount:.2f} successful.")
        self.append_daily_transaction("01", account.account_name, acc_number, amount)

    # deposit
    # account_number if in admin
    # amount
    def deposit(self, acc_number, amount):
        if not self.current_user:
            print("Error: Not logged in.")
            return

        if acc_number not in self.accounts:
            print("Error: Invalid account.")
            return

        account = self.accounts[acc_number]

        if account.status != "A":
            print("Error: Account disabled.")
            return

        if amount <= 0:
            print("Error: Invalid amount.")
            return

        account.edit_balance(account.get_balance() + amount)
        print(f"Deposit of ${amount:.2f} successful.")
        # deposited funds not usable this session (no change to available balance semantics)
        self.append_daily_transaction("04", account.account_name, acc_number, amount)

    # transfer
    # account holders name if logged in as admin
    # from_account_number that will be transferred from
    # to_account_number that will be transferred to
    # amount
    def transfer(self, from_acc, to_acc, amount):
        if not self.current_user:
            print("Error: Not logged in.")
            return

        if from_acc not in self.accounts or to_acc not in self.accounts:
            print("Error: Invalid account.")
            return

        sender = self.accounts[from_acc]
        receiver = self.accounts[to_acc]

        if sender.status != "A" or receiver.status != "A":
            print("Error: Account disabled.")
            return

        if not self.admin and amount > 1000.00:
            print("Error: Maximum transfer is $1000.00.")
            return

        new_sender_balance = sender.get_balance() - amount
        if new_sender_balance < 0:
            print("Error: Insufficient funds.")
            return

        sender.edit_balance(new_sender_balance)
        receiver.edit_balance(receiver.get_balance() + amount)

        print(f"Transfer of ${amount:.2f} successful.")
        self.append_daily_transaction("02", sender.account_name, from_acc, amount)
        self.append_daily_transaction("02", receiver.account_name, to_acc, amount)

    # paybill
    # ask for account holder's name if logged in as admin
    # account_number that will be paid from
    # payee name
    # amount
    def paybill(self, acc_number, payee, amount):
        if not self.current_user:
            print("Error: Not logged in.")
            return

        if acc_number not in self.accounts:
            print("Error: Invalid account.")
            return

        account = self.accounts[acc_number]

        if account.status != "A":
            print("Error: Account disabled.")
            return

        valid_companies = {
            "The Bright Light Electric Company (EC)",
            "Credit Card Company Q (CQ)",
            "Fast Internet, Inc. (FI)"
        }

        if payee not in valid_companies:
            print("Error: Invalid bill payment company.")
            return

        if amount <= 0:
            print("Error: Invalid amount.")
            return

        if not self.admin and amount > 2000.00:
            print("Error: Maximum payment is $2000.00.")
            return

        new_balance = account.get_balance() - amount
        if new_balance < 0:
            print("Error: Insufficient funds.")
            return

        account.edit_balance(new_balance)
        print(f"Payment of ${amount:.2f} successful.")
        self.append_daily_transaction("03", account.account_name, acc_number, amount, payee)
    
    # ------------------------
    # ADMIN COMMANDS
    # ------------------------

    # create an account (Admin only)
    # ask for name
    # ask for initial balance
    def create(self, acc_number, name, balance):
        if not self.current_user or not self.admin:
            print("Error: Unauthorized.")
            return

        if len(name) > 20:
            print("Error: Account holder name exceeds 20 characters.")
            return

        if balance > 99999.99:
            print("Error: Initial balance exceeds $99999.99.")
            return

        if acc_number in self.accounts:
            print("Error: Account number already exists.")
            return

        self.accounts[acc_number] = BankAccount(name, acc_number, balance)
        print("Account created successfully.")
        self.append_daily_transaction("05", name, acc_number, balance)

    # delete an account (Admin only)
    # ask for name
    # ask for account number
    def delete(self, acc_number):
        if not self.current_user or not self.admin:
            print("Error: Unauthorized.")
            return

        if acc_number not in self.accounts:
            print("Error: Account holder or account number does not exist.")
            return

        account = self.accounts[acc_number]
        name = account.account_name

        del self.accounts[acc_number]

        print("Account deleted successfully.")
        self.append_daily_transaction("06", name, acc_number)

    # disable an account (Admin only)
    # ask for name
    # ask for account number
    def disable(self, acc_number):
        if not self.current_user or not self.admin:
            print("Error: Unauthorized.")
            return

        if acc_number not in self.accounts:
            print("Error: Account holder or account number does not exist.")
            return

        account = self.accounts[acc_number]
        account.status = "D"

        print("Account disabled successfully.")
        self.append_daily_transaction("07", account.account_name, acc_number)

    # Switch from student plan to non-student plan (Admin only)
    # changeplan
    # name
    # account number
    def changeplan(self, acc_number):
        if not self.current_user or not self.admin:
            print("Error: Unauthorized.")
            return

        if acc_number not in self.accounts:
            print("Error: Account holder or account number does not exist.")
            return

        account = self.accounts[acc_number]
        account.payment_plan = "NP"

        print("Payment plan changed successfully.")
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
