# account.py
"""
Defines the Account data class used by the Back End.

Mirrors the fields read/written by the Front End's BankAccount class,
but adds a transaction_count field (needed by the Master Accounts File)
and plan field (student 'S' / non-student 'N', used for fee calculation).

Current Accounts File format  (37 chars per line):
  [0:5]   account number      e.g. "00001"
  [5:25]  account name        e.g. "John_Doe____________"  (underscores fill spaces)
  [25]    status              'A' or 'D'
  [26:34] balance             e.g. "00050.00"
  [34]    plan                'S' (student) or 'N' (non-student)
  [35:37] padding             "  " (two spaces)
"""

# ---------------------------------------------------------------------------
# Fee constants (debited once per transaction)
# ---------------------------------------------------------------------------
FEE_STUDENT     = 0.05   # $0.05 per transaction on student plan
FEE_NON_STUDENT = 0.10   # $0.10 per transaction on non-student plan


class Account:
    """
    Represents a single bank account in the Back End.

    Attributes:
        number          (str)  : 5-digit zero-padded account number.
        name            (str)  : Account holder name (up to 20 characters,
                                 stored internally with spaces, not underscores).
        status          (str)  : 'A' (active) or 'D' (disabled).
        balance         (float): Current balance in Canadian dollars.
        transaction_count (int): Total transactions applied today (for master file).
        plan            (str)  : 'S' (student) or 'N' (non-student).
    """

    def __init__(self, number: str, name: str, status: str,
                 balance: float, transaction_count: int = 0, plan: str = 'S'):
        """
        Initialises an Account with all required fields.

        Args:
            number            (str)  : 5-digit account number.
            name              (str)  : Account holder name (spaces, not underscores).
            status            (str)  : 'A' or 'D'.
            balance           (float): Account balance.
            transaction_count (int)  : Number of transactions so far today.
            plan              (str)  : 'S' or 'N'; defaults to student plan.
        """
        self.number            = number
        self.name              = name
        self.status            = status
        self.balance           = round(float(balance), 2)
        self.transaction_count = transaction_count
        self.plan              = plan

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    def is_active(self) -> bool:
        """Returns True when this account's status is active ('A')."""
        return self.status == 'A'

    def is_student_plan(self) -> bool:
        """Returns True when this account is on the student plan ('S')."""
        return self.plan == 'S'

    # ------------------------------------------------------------------
    # Fee helper
    # ------------------------------------------------------------------

    def transaction_fee(self) -> float:
        """Returns the per-transaction fee amount based on the account's plan."""
        return FEE_STUDENT if self.is_student_plan() else FEE_NON_STUDENT

    # ------------------------------------------------------------------
    # Formatting for output files
    # ------------------------------------------------------------------

    def to_current_accounts_line(self) -> str:
        """
        Formats this account as a 37-character line for the Current Accounts File
        consumed by tomorrow's Front End.

        Name is written with underscores replacing spaces (matching Front End
        load_accounts parsing which calls .replace('_', ' ')).

        Returns:
            str: 37-character string (no trailing newline).
        """
        num_field     = self.number.zfill(5)
        # Name: replace spaces with underscores, left-justified, underscore-padded to 20
        name_field    = self.name.replace(' ', '_')[:20].ljust(20, '_')
        balance_field = f"{self.balance:08.2f}"
        # Format: NNNNN space A*20 space S space PPPPPPPP = 37 chars
        line = f"{num_field} {name_field} {self.status} {balance_field}"
        return line  # 5+1+20+1+1+1+8 = 37 chars

    def to_master_accounts_line(self) -> str:
        """
        Formats this account as a 42-character line for the Master Bank Accounts File.

        Master format: NNNNN AAAAAAAAAAAAAAAAAAAA S NNNNN.PP TTTT  (42 chars)
          [0:5]   account number
          [5]     space
          [6:26]  name (space-padded, spaces not underscores)
          [26]    space
          [27]    status
          [28]    space
          [29:37] balance "NNNNN.PP"
          [37]    space
          [38:42] transaction count

        Returns:
            str: 42-character string (no trailing newline).
        """
        num_field     = self.number.zfill(5)
        # Name: replace spaces with underscores, left-justified, underscore-padded
        name_field    = self.name.replace(' ', '_')[:20].ljust(20, '_')
        balance_field = f"{self.balance:08.2f}"
        trans_field   = str(self.transaction_count).zfill(4)
        line = f"{num_field} {name_field} {self.status} {balance_field} {trans_field}"
        return line  # 5+1+20+1+1+1+8+1+4 = 42 chars

    def __repr__(self) -> str:
        """Returns a compact developer-readable summary."""
        return (f"Account({self.number}, '{self.name}', {self.status}, "
                f"${self.balance:.2f}, plan={self.plan}, tx={self.transaction_count})")