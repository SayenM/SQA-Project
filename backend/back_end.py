# back_end.py
"""
Banking System Back End  -  CSCI 3060U Phase #4
================================================
Purpose:
    Reads the Current Accounts File and the Merged Transaction File produced
    by one or more Front End sessions, applies all transactions, and writes:
      1. A new Current Accounts File   (for tomorrow's Front End runs)
      2. A new Master Accounts File    (permanent daily record of all accounts)

    If the output current accounts path is the same as the input path, the
    backend writes to a temporary file first, then replaces the original once
    all reading is complete -- preventing the file from being wiped mid-read.

    Constraint violations (e.g. negative balance, duplicate account number) are
    printed to the terminal; the offending transaction is skipped and processing
    continues.  Fatal errors (bad files, unknown transaction codes) print a
    message and exit immediately.

Input Files  (command-line arguments):
    1. current_accounts.txt  -  37-char fixed-width lines produced by the Front End.
    2. daily_transactions.txt - 40-char fixed-width lines from all Front End sessions,
                                with one end-of-session line (code "00") per session.

Output Files (command-line arguments):
    3. current_accounts.txt  -  Updated active accounts (can be same file as input).
    4. master_accounts.txt   -  Full account record (active + disabled) in 42-char format.

How to Run:
    python back_end.py <current_accounts> <transactions> <current_accounts> <master_accounts>

Example:
    python back_end.py ../current_accounts.txt ../daily_transactions.txt
                       ../current_accounts.txt ../master_accounts.txt
"""

import sys
import os
import tempfile
from file_handler           import FileHandler
from account_manager        import AccountManager
from transaction_processor  import TransactionProcessor


def main():
    """
    Orchestrates the Back End pipeline:
      1. Validate command-line arguments.
      2. Load current accounts from the Current Accounts File.
      3. Load all transactions from the Merged Transaction File.
      4. Build the in-memory account store.
      5. Apply every transaction, enforcing constraints and charging fees.
      6. Write the new Current Accounts File (active accounts only).
         If the output path matches the input path, write to a temp file
         first then atomically replace the original.
      7. Write the new Master Accounts File (all accounts).
    """
    # -- 1. Validate arguments --------------------------------------------
    if len(sys.argv) != 5:
        print("Usage: python back_end.py <current_accounts> <transactions> "
              "<current_accounts> <master_accounts>")
        sys.exit(1)

    current_accounts_path = sys.argv[1]   # Input:  today's active accounts
    transactions_path     = sys.argv[2]   # Input:  merged transaction file
    new_current_path      = sys.argv[3]   # Output: updated current accounts
    new_master_path       = sys.argv[4]   # Output: full master accounts record

    # -- 2 & 3. Load ALL input files before writing anything --------------
    # Both files are fully read into memory here so that writing the output
    # current accounts file (which may be the same path) is safe.
    file_handler = FileHandler()
    accounts     = file_handler.load_current_accounts(current_accounts_path)
    transactions = file_handler.load_transactions(transactions_path)

    # -- 4. Build in-memory account store ---------------------------------
    account_manager = AccountManager(accounts)

    # -- 5. Apply all transactions ----------------------------------------
    processor = TransactionProcessor(account_manager)
    processor.process_all(transactions)

    # -- 6. Write the new Current Accounts File ---------------------------
    all_accounts = account_manager.get_all_accounts()

    # Detect if we are overwriting the input file.
    # If so, write to a temp file in the same directory first, then replace
    # the original -- this is safe even if something goes wrong mid-write.
    input_resolved  = os.path.realpath(current_accounts_path)
    output_resolved = os.path.realpath(new_current_path)

    if input_resolved == output_resolved:
        # Write to a temporary file in the same directory as the target
        target_dir = os.path.dirname(new_current_path) or '.'
        tmp_fd, tmp_path = tempfile.mkstemp(dir=target_dir, suffix='.tmp')
        os.close(tmp_fd)
        try:
            file_handler.write_current_accounts(tmp_path, all_accounts)
            os.replace(tmp_path, new_current_path)  # atomic replace
        except Exception as e:
            # Clean up the temp file if something went wrong
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            print(f"FATAL ERROR: Could not write current accounts file: {e}")
            sys.exit(1)
    else:
        file_handler.write_current_accounts(new_current_path, all_accounts)

    # -- 7. Write the new Master Accounts File ----------------------------
    file_handler.write_master_accounts(new_master_path, all_accounts)

    print("Back End complete.")
    print(f"  Current accounts updated -> {new_current_path}")
    print(f"  Master accounts written  -> {new_master_path}")


if __name__ == "__main__":
    main()