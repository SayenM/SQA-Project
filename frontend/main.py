# main.py
'''
The overall entry point for the banking application. Initializes the FrontEnd and Menu,
then enters a loop to read user commands from the console and process them.
'''
from menu_transactions import FrontEnd
from menu import Menu

def main():
    frontend = FrontEnd()
    frontend.load_accounts("../current_accounts.txt")

    menu = Menu("user", frontend)   # pass FrontEnd object to Menu
    # Main loop to read user commands and process them.
    while True:
      try:
        command = input()
        menu.handle_command(command)
      except EOFError:
        break

if __name__ == "__main__":
    main()
