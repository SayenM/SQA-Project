from read import read_old_bank_accounts
from write import write_new_current_accounts
from back_end import process_transactions, write_master_accounts

'''
Handels accounts and transactions going into the back end
Calls methods to write master accounts and new current accounts output files. 
'''
def main():
    master_file = "old_master_accounts.txt"
    transaction_file = "merged_transactions.txt"
    new_master = "new_master_accounts.txt"
    new_current = "new_current_accounts.txt"

    # Read in old accounts and make dictonary
    old_accounts = read_old_bank_accounts(master_file)
    accounts = {acc['account_number']: acc for acc in old_accounts}

    # Account for the transactions
    process_transactions(accounts, transaction_file)

    # Get accounts and sort in ascending order by account number
    account_list = list(accounts.values())
    account_list.sort(key=lambda x: int(x['account_number']))

    # Write both of the output files
    write_master_accounts(account_list, new_master)
    write_new_current_accounts(account_list, new_current)

if __name__ == "__main__":
    main()