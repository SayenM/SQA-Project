# menu.py
class Menu:
    # Handles console input/output and calls FrontEnd for transactions.

    def __init__(self, menu_type, frontend):
        self._type = menu_type
        self.frontend = frontend

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value

    def handle_command(self, command: str):
        parts = command.strip().split()
        if not parts:
            return

        action = parts[0].upper()

        if action == "LOGIN":
            username = parts[1]
            password = parts[2] if len(parts) > 2 else ""
            self.frontend.login(username, password)

        elif action == "LOGOUT":
            self.frontend.logout()

        elif action == "WITHDRAW":
            acc, amount = parts[1], float(parts[2])
            self.frontend.withdraw(acc, amount)

        elif action == "DEPOSIT":
            acc, amount = parts[1], float(parts[2])
            self.frontend.deposit(acc, amount)

        elif action == "TRANSFER":
            acc1, acc2, amount = parts[1], parts[2], float(parts[3])
            self.frontend.transfer(acc1, acc2, amount)

        elif action == "PAYBILL":
            acc, payee, amount = parts[1], parts[2], float(parts[3])
            self.frontend.paybill(acc, payee, amount)

        elif action == "CREATE":
            acc_number, name, balance = parts[1], parts[2], float(parts[3])
            self.frontend.create(acc_number, name, balance)

        elif action == "DELETE":
            acc_number = parts[1]
            self.frontend.delete(acc_number)

        elif action == "DISABLE":
            acc_number = parts[1]
            self.transactions.disable(acc_number)

        elif action == "CHANGEPLAN":
            acc_number = parts[1]
            self.transactions.changeplan(acc_number)
