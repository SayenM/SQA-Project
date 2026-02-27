#!/bin/bash

EXPECTED_DIR="test_IO/expected"
RESULTS_DIR="test_IO/results"
PROGRAM="python main.py"

mkdir -p "$RESULTS_DIR"

pass_count=0
fail_count=0

for inputfile in "$EXPECTED_DIR"/in/*_in.txt; do
    name=$(basename "$inputfile" _in.txt)
    expected="$EXPECTED_DIR/out/${name}_out.txt"
    outputfile="$RESULTS_DIR/${name}_result.txt"

    echo "Running: $name"
    $PROGRAM < "$inputfile" > "$outputfile"

    if diff -q "$expected" "$outputfile" > /dev/null; then
        echo "PASS: $name"
        ((pass_count++))
    else
        echo "FAIL: $name"
        diff "$expected" "$outputfile"
        ((fail_count++))
    fi

    echo "-------------------------"
done

echo "Tests complete."
echo "Passed: $pass_count"
echo "Failed: $fail_count"