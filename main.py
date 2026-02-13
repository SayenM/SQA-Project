# main.py
from menu_transactions import FrontEnd
from menu import Menu

def main():
    frontend = FrontEnd()
    frontend.load_accounts("current_accounts.txt")

    menu = Menu(frontend)   # pass FrontEnd object to Menu
    menu.run()              # starts console interaction

if __name__ == "__main__":
    main()
