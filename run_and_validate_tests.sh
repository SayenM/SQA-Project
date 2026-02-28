#!/bin/bash

# Location of expected IO and location to store results
EXPECTED_DIR="test_IO/expected"
RESULTS_DIR="test_IO/results"

# Commmand to run program
PROGRAM="python main.py"

# Create results directory if it does no exist
mkdir -p "$RESULTS_DIR"

pass_count=0
fail_count=0

# Loop over all input files
for inputfile in "$EXPECTED_DIR"/in/*_in.txt; do
    # Get name of test
    name=$(basename "$inputfile" _in.txt)

    # Get the expected output path
    expected="$EXPECTED_DIR/out/${name}_out.txt"

    # Get path to save test output
    outputfile="$RESULTS_DIR/${name}_result.txt"

    # Display the current test
    echo "Running: $name"
    # Get input to run the program and direct output to results file
    $PROGRAM < "$inputfile" > "$outputfile"

    # Tests for differences in expected vs actual output
    if diff -q "$expected" "$outputfile" > /dev/null; then
        echo "PASS: $name"
        ((pass_count++))
    else
        echo "FAIL: $name"

        # Show the difference in expected and actual output
        diff "$expected" "$outputfile"
        ((fail_count++))
    fi

    echo "-------------------------"
done

# Tests summary
echo "Tests complete."
echo "Passed: $pass_count"
echo "Failed: $fail_count"