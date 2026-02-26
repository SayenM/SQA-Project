"""
Handles console input/output and calls FrontEnd for transactions.
The Menu class processes user commands and interacts with the FrontEnd to perform banking operations.
"""

class Menu:
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
        action = command.strip().lower()
        if not action:
            return

        if action == "login":
            session_type = input().strip()
            name = ""
            if session_type == "standard":
                name = input().strip()
            self.frontend.login(session_type, name)

        elif action == "logout":
            self.frontend.logout()

        elif action == "withdrawal":
            acc = input().strip()
            try:
                amount = float(input())
            except ValueError:
                print("Error: Invalid amount.")
                return
            self.frontend.withdraw(acc, amount)

        elif action == "deposit":
            acc = input().strip()
            try:
                amount = float(input())
            except ValueError:
                print("Error: Invalid amount.")
                return
            self.frontend.deposit(acc, amount)

        elif action == "transfer":
            from_acc = input().strip()
            to_acc = input().strip()
            try:
                amount = float(input())
            except ValueError:
                print("Error: Invalid amount.")
                return
            self.frontend.transfer(from_acc, to_acc, amount)

        elif action == "paybill":
            acc = input().strip()
            payee = input().strip()
            try:
                amount = float(input())
            except ValueError:
                print("Error: Invalid amount.")
                return
            self.frontend.paybill(acc, payee, amount)

        elif action == "create":
            name = input().strip()
            try:
                balance = float(input())
            except ValueError:
                print("Error: Invalid balance.")
                return
            # account number assigned by backend or tests; pass empty or generated
            self.frontend.create("", name, balance)

        elif action == "delete":
            acc = input().strip()
            self.frontend.delete(acc)

        elif action == "disable":
            acc = input().strip()
            self.frontend.disable(acc)

        elif action == "changeplan":
            acc = input().strip()
            self.frontend.changeplan(acc)

        else:
            print("Error: Unknown command.")