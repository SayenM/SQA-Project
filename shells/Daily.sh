#!/bin/bash
# =============================================================================
# daily.sh
# CSCI 3060U – Phase #6   Daily Banking System Script
#
# Usage:
#   bash daily.sh <session1_input> <session2_input> ... <sessionN_input>
#
# What it does:
#   1. Runs the Front End once per input file, each producing a separate
#      Daily Bank Account Transaction File (transactions_session_N.txt).
#   2. Concatenates all session files into one Merged Daily Bank Account
#      Transaction File (daily_transactions.txt).
#   3. Runs the Back End with the merged file as input, updating
#      current_accounts.txt and writing master_accounts.txt.
#
# Directory layout assumed:
#   ./                        <- run script from here (project root)
#   ./frontend/main.py
#   ./backend/back_end.py
#   ./current_accounts.txt    <- read by Front End and Back End
#   ./master_accounts.txt     <- written by Back End
#   ./daily_transactions.txt  <- merged transaction file (rebuilt each run)
# =============================================================================

set -e   # Exit immediately on any error

# ---------------------------------------------------------------------------
# Validate arguments
# ---------------------------------------------------------------------------
if [ "$#" -lt 1 ]; then
    echo "Usage: bash daily.sh <session1_input> [session2_input] ..."
    exit 1
fi

echo "========================================"
echo " DAILY BANKING SYSTEM RUN"
echo " $(date)"
echo "========================================"

# ---------------------------------------------------------------------------
# Step 1: Run the Front End for each session input file
#         Each session writes its own transactions file.
# ---------------------------------------------------------------------------
SESSION_FILES=()   # will hold paths of per-session transaction files

SESSION_NUM=0
for INPUT_FILE in "$@"; do
    SESSION_NUM=$((SESSION_NUM + 1))

    if [ ! -f "$INPUT_FILE" ]; then
        echo "ERROR: Input file not found: $INPUT_FILE"
        exit 1
    fi

    SESSION_TX="transactions_session_${SESSION_NUM}.txt"

    echo ""
    echo "--- Session $SESSION_NUM: $INPUT_FILE ---"

    # The Front End is hardcoded to write to ../daily_transactions.txt relative
    # to the frontend/ directory. We clear it before each session so that only
    # the current session's transactions are captured, then copy the result to
    # a uniquely named file to preserve it before the next session overwrites it.
    > daily_transactions.txt

    # Run the Front End, feeding the input file via stdin redirect.
    (cd frontend && python main.py < "../$INPUT_FILE")

    # daily_transactions.txt now contains exactly this session's transactions.
    # Copy it to a uniquely named session file before the next session overwrites it.
    cp daily_transactions.txt "$SESSION_TX"
    SESSION_FILES+=("$SESSION_TX")

    echo "  -> Session $SESSION_NUM transactions saved to $SESSION_TX"
done

# ---------------------------------------------------------------------------
# Step 2: Concatenate all per-session files into the Merged Transaction File
# ---------------------------------------------------------------------------
echo ""
echo "--- Merging ${#SESSION_FILES[@]} session file(s) ---"
> daily_transactions.txt   # clear/create the merged file

for SESSION_FILE in "${SESSION_FILES[@]}"; do
    cat "$SESSION_FILE" >> daily_transactions.txt
    echo "  Appended $SESSION_FILE"
done

echo "  -> Merged file: daily_transactions.txt"

# ---------------------------------------------------------------------------
# Step 3: Run the Back End with the merged transaction file
# ---------------------------------------------------------------------------
echo ""
echo "--- Running Back End ---"
python backend/back_end.py \
    current_accounts.txt \
    daily_transactions.txt \
    current_accounts.txt \
    master_accounts.txt

echo ""
echo "========================================"
echo " DAILY RUN COMPLETE"
echo " Current accounts : current_accounts.txt"
echo " Master accounts  : master_accounts.txt"
echo " Merged tx file   : daily_transactions.txt"
echo "========================================"