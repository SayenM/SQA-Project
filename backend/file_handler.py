# file_handler.py
"""
Handles all file reading and writing for the Banking System Back End.

Reads:
  - Current Accounts File  (37-char fixed-width lines, written by the Front End)
  - Merged Transaction File (40-char fixed-width lines, written by the Front End)

Writes:
  - New Current Accounts File  (37-char lines, for tomorrow's Front End)
  - New Master Accounts File   (42-char lines, permanent record)

Current Accounts File line layout (37 chars):
  [0:5]   account number
  [5:25]  name (20 chars, underscores instead of spaces)
  [25]    status  'A' or 'D'
  [26:34] balance "NNNNN.PP"
  [34]    plan    'S' or 'N'  (Back End writes this; Front End ignores it safely)
  [35:37] padding "  "

Transaction File line layout (40 chars, from Front End append_daily_transaction):
  [0:2]   transaction code  e.g. "01"
  [2:22]  account name      (20 chars, underscores instead of spaces)
  [22:27] account number    (5 chars)
  [27:35] amount            "NNNNN.PP" (8 chars)
  [35:40] misc              (5 chars: payee abbreviation or spaces)

End-of-session sentinel: code "00", rest is zeros/spaces.
"""

import sys
from account import Account


# ---------------------------------------------------------------------------
# Slice constants — Current Accounts File (spec format, 37 chars)
# NNNNN_AAAAAAAAAAAAAAAAAAAA_S_PPPPPPPP
# [0:5]=number [5]=space [6:26]=name [26]=space [27]=status [28]=space [29:37]=balance
# ---------------------------------------------------------------------------
_CA_NUMBER  = slice(0,  5)    # account number
_CA_NAME    = slice(6,  26)   # name (underscore-padded, 20 chars)
_CA_STATUS  = slice(27, 28)   # status char
_CA_BALANCE = slice(29, 37)   # balance "NNNNN.PP"

# ---------------------------------------------------------------------------
# Slice constants — Transaction File (spec format, 40 chars)
# CC_AAAAAAAAAAAAAAAAAAAA_NNNNN_PPPPPPPP_MM
# [0:2]=code [2]=space [3:23]=name [23]=space [24:29]=number [29]=space [30:38]=amount [38:40]=misc
# ---------------------------------------------------------------------------
_TX_CODE    = slice(0,  2)    # 2-char transaction code
_TX_NAME    = slice(3,  23)   # 20-char account name (underscore-padded)
_TX_NUMBER  = slice(24, 29)   # 5-char account number
_TX_AMOUNT  = slice(30, 38)   # 8-char amount "NNNNN.PP"
_TX_MISC    = slice(38, 40)   # 2-char miscellaneous field

# Sentinel code that marks the end of one Front End session
END_OF_SESSION_CODE = "00"

# EOF marker account number in the Current Accounts File
EOF_ACCOUNT_NUMBER = "00000"


class FileHandler:
    """
    Reads and writes all files for the Banking System Back End.

    All methods report fatal errors to the terminal and exit immediately
    if a file cannot be opened or a line is malformed.
    """

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def load_current_accounts(self, filepath: str) -> list:
        """
        Reads the Current Accounts File and returns a list of Account objects.

        Stops reading when the EOF marker account "00000" is encountered.
        Logs a fatal error and exits if the file cannot be opened.

        Args:
            filepath (str): Path to the current accounts file.

        Returns:
            list[Account]: All accounts found before the EOF marker.
        """
        accounts = []
        try:
            with open(filepath, 'r') as f:
                for line_num, raw_line in enumerate(f, start=1):
                    line = raw_line.rstrip('\n').ljust(37)

                    # Spec format: NNNNN_AAAAAAAAAAAAAAAAAAAA_S_PPPPPPPP (37 chars)
                    # [0:5]=number [5]=space [6:26]=name [26]=space [27]=status [28]=space [29:37]=balance
                    number = line[_CA_NUMBER]

                    # Stop at the EOF marker
                    if number == EOF_ACCOUNT_NUMBER:
                        break

                    name        = line[_CA_NAME].replace('_', ' ').strip()
                    status      = line[_CA_STATUS] if len(line) > 27 else 'A'
                    balance_str = line[_CA_BALANCE].strip() if len(line) >= 37 else '0.00'

                    try:
                        balance = float(balance_str)
                    except ValueError:
                        print(f"FATAL ERROR: Cannot parse balance '{balance_str}' "
                              f"on line {line_num} of '{filepath}'. Aborting.")
                        sys.exit(1)

                    # No plan field in spec format; default all accounts to student plan
                    plan = 'S'

                    accounts.append(Account(number, name, status, balance, 0, plan))

        except OSError as e:
            print(f"FATAL ERROR: Cannot open accounts file '{filepath}': {e}")
            sys.exit(1)

        return accounts

    def load_transactions(self, filepath: str) -> list:
        """
        Reads the Merged Transaction File and returns every transaction as a dict.

        The file may contain multiple Front End sessions, each terminated by an
        end-of-session line (code "00").  ALL non-sentinel transactions across
        ALL sessions are collected and returned together.

        Logs a fatal error and exits if the file cannot be opened.

        Transaction dict keys:
            'code'   (str)  : 2-char transaction code.
            'name'   (str)  : Account holder name (spaces, not underscores).
            'number' (str)  : 5-char account number.
            'amount' (float): Dollar amount.
            'misc'   (str)  : Miscellaneous field (stripped of whitespace).

        Args:
            filepath (str): Path to the merged transaction file.

        Returns:
            list[dict]: All non-sentinel transactions from all sessions.
        """
        transactions = []
        try:
            with open(filepath, 'r') as f:
                for line_num, raw_line in enumerate(f, start=1):
                    line = raw_line.rstrip('\n').ljust(40)   # pad defensively

                    code = line[_TX_CODE]

                    # Skip end-of-session sentinels; continue reading (more sessions may follow)
                    if code == END_OF_SESSION_CODE:
                        continue

                    # Skip blank or malformed lines
                    if len(line.strip()) == 0:
                        continue

                    name   = line[_TX_NAME].replace('_', ' ').strip()
                    number = line[_TX_NUMBER].strip()
                    misc   = line[_TX_MISC].strip()

                    try:
                        amount = float(line[_TX_AMOUNT])
                    except ValueError:
                        print(f"FATAL ERROR: Cannot parse amount on line {line_num} "
                              f"of '{filepath}'. Aborting.")
                        sys.exit(1)

                    transactions.append({
                        'code':   code,
                        'name':   name,
                        'number': number,
                        'amount': amount,
                        'misc':   misc,
                    })

        except OSError as e:
            print(f"FATAL ERROR: Cannot open transaction file '{filepath}': {e}")
            sys.exit(1)

        return transactions

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def write_current_accounts(self, filepath: str, accounts: list) -> None:
        """
        Writes the New Current Accounts File for tomorrow's Front End.

        Only active accounts are included.  Accounts are sorted in ascending
        account-number order.  An EOF marker line (account "00000") is written last.

        Args:
            filepath (str)  : Destination file path.
            accounts (list) : All Account objects (active and disabled).
        """
        active = sorted(
            [a for a in accounts if a.is_active()],
            key=lambda a: a.number
        )
        try:
            with open(filepath, 'w') as f:
                for account in active:
                    f.write(account.to_current_accounts_line() + '\n')
                # Write the EOF marker in the same 37-char format
                # EOF marker in spec format: NNNNN_A*20_S_PPPPPPPP
                eof_line = "00000 END_OF_FILE_________ A 00000.00"
                f.write(eof_line[:37] + '\n')
        except OSError as e:
            print(f"FATAL ERROR: Cannot write current accounts file '{filepath}': {e}")
            sys.exit(1)

    def write_master_accounts(self, filepath: str, accounts: list) -> None:
        """
        Writes the New Master Accounts File (permanent record of all accounts).

        Includes ALL accounts (active and disabled).  Sorted ascending by
        account number.

        Args:
            filepath (str)  : Destination file path.
            accounts (list) : All Account objects.
        """
        sorted_accounts = sorted(accounts, key=lambda a: a.number)
        try:
            with open(filepath, 'w') as f:
                for account in sorted_accounts:
                    f.write(account.to_master_accounts_line() + '\n')
        except OSError as e:
            print(f"FATAL ERROR: Cannot write master accounts file '{filepath}': {e}")
            sys.exit(1)