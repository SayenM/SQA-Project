#!/bin/bash

EXPECTED_DIR="test_IO/expected"
RESULTS_DIR="test_IO/results"

for expected in "$EXPECTED_DIR"/out/*_out.txt; do
    name=$(basename "$expected" _out.txt)
    result="$RESULTS_DIR/${name}_out.txt"

    echo "Checking: $name"
    diff "$expected" "$result"
done

echo "Validation complete."