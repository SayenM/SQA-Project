#!/bin/bash
# =============================================================================
# weekly.sh
# CSCI 3060U – Phase #6   Weekly Banking System Script
#
# Usage:
#   bash weekly.sh
#
# What it does:
#   Runs daily.sh seven times, once per day (Monday–Sunday).
#   Each day uses a different set of transaction session input files.
#   The Current Accounts File output from each day becomes the input
#   for the following day, simulating a full week of bank operation.
#
# Transaction input files (in ./inputs/):
#   day1_session1.txt  day1_session2.txt
#   day2_session1.txt  day2_session2.txt
#   ...
#   day7_session1.txt  day7_session2.txt
#
# Directory layout assumed:
#   ./                        <- run script from here (project root)
#   ./daily.sh
#   ./frontend/main.py
#   ./backend/back_end.py
#   ./inputs/dayN_sessionM.txt
#   ./current_accounts.txt    <- seed file must exist before running
# =============================================================================

set -e   # Exit immediately on any error

DAYS=("Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday" "Sunday")

# ---------------------------------------------------------------------------
# Verify the seed current accounts file exists
# ---------------------------------------------------------------------------
if [ ! -f "current_accounts.txt" ]; then
    echo "ERROR: current_accounts.txt not found in project root."
    echo "       Please provide a seed current accounts file before running."
    exit 1
fi

# ---------------------------------------------------------------------------
# Verify all input files exist before starting the week
# ---------------------------------------------------------------------------
echo "Checking input files..."
for DAY_NUM in 1 2 3 4 5 6 7; do
    for SESSION_NUM in 1 2; do
        INPUT="inputs/day${DAY_NUM}_session${SESSION_NUM}.txt"
        if [ ! -f "$INPUT" ]; then
            echo "ERROR: Missing input file: $INPUT"
            exit 1
        fi
    done
done
echo "All input files found."
echo ""

# ---------------------------------------------------------------------------
# Archive directory for weekly outputs
# ---------------------------------------------------------------------------
WEEK_DIR="week_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$WEEK_DIR"
echo "Weekly output archive: $WEEK_DIR/"
echo ""

# ---------------------------------------------------------------------------
# Run one day at a time
# ---------------------------------------------------------------------------
for DAY_NUM in 1 2 3 4 5 6 7; do
    DAY_NAME="${DAYS[$((DAY_NUM - 1))]}"

    echo "###################################################"
    echo "# DAY $DAY_NUM – $DAY_NAME"
    echo "###################################################"

    # Run the daily script located in the same directory as this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/daily.sh" \
        "inputs/day${DAY_NUM}_session1.txt" \
        "inputs/day${DAY_NUM}_session2.txt"

    # Archive this day's outputs so they are not overwritten tomorrow
    cp current_accounts.txt  "$WEEK_DIR/day${DAY_NUM}_current_accounts.txt"
    cp master_accounts.txt   "$WEEK_DIR/day${DAY_NUM}_master_accounts.txt"
    cp daily_transactions.txt "$WEEK_DIR/day${DAY_NUM}_daily_transactions.txt"

    # Archive the per-session transaction files for this day
    for SESSION_NUM in 1 2; do
        SESSION_FILE="transactions_session_${SESSION_NUM}.txt"
        if [ -f "$SESSION_FILE" ]; then
            cp "$SESSION_FILE" "$WEEK_DIR/day${DAY_NUM}_${SESSION_FILE}"
        fi
    done

    echo ""
    echo "Day $DAY_NUM outputs archived to $WEEK_DIR/day${DAY_NUM}_*"
    echo ""
done

# ---------------------------------------------------------------------------
# Weekly summary
# ---------------------------------------------------------------------------
echo "###################################################"
echo "# WEEKLY RUN COMPLETE"
echo "# $(date)"
echo "#"
echo "# Final current accounts : current_accounts.txt"
echo "# Final master accounts  : master_accounts.txt"
echo "# All daily archives     : $WEEK_DIR/"
echo "###################################################"