class bank_account:

  def __init__(self, acc_name: str, acc_number: str, new_balance: float):
    self.account_name = acc_name
    self.account_number = acc_number
    self.balance = new_balance

  def get_balance(self) -> float:
    return self.balance
  
  def edit_balance(self,balance:float) -> float:
    self.balance = float(balance)
    return self.balance

class menu:

  def __init__(self):
    self.is_logged_in = False
    self.admin = False
    self.name = ""
    self.accounts = {}

  
  def login(self, user: str, password: str):
    self.is_logged_in = True
    self.name = user
    if user.lower().startswith("admin"):
      self.admin = True
    else: False
    

  def logout(self):
    self.is_logged_in = False
    self.admin = False
    self.name = ""

  def withdraw(self, current_account: str, withdrawn: float):
    account = self.accounts[current_account]
    account.edit_balance(account.get_balance() - withdrawn)

  def deposit(self, current_account: str, deposit: float):
    account = self.accounts[current_account]
    account = account.editbalance(account.get_balance() + deposit)

  def transfer(self, account_one: str, account_two: str, transferred: float):
    sender = self.accounts[account_one]
    receiver = self.accounts[account_two]
    transfer = float(transferred)
    sender.edit_balance(sender.get_balance() - transfer)
    receiver.edit_balance(receiver.get_balance() + transfer)

  def paybill(self, account_paid: str, payee: str, paid: float):
    account = self.accounts[account_paid]
    pay = float(paid)
    account.edit_balance(account.get_balance() - pay)
    print(f"{paid} paid to {payee} from Account: {account_paid}")

  def create(self, account: str, name: str, password: str, balance: float):
    self.accounts[account] = bank_account(name, account, float(balance))

  def delete(self, account: str):
    del self.accounts[account]

  #TODO disable method, changeplan in class:menu