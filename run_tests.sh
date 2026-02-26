#!/bin/bash

EXPECTED_DIR="test_IO/expected"
RESULTS_DIR="test_IO/results"
PROGRAM="python main.py"

mkdir -p "$RESULTS_DIR"

for inputfile in "$EXPECTED_DIR"/in/*_in.txt; do
    name=$(basename "$inputfile" _in.txt)
    outputfile="$RESULTS_DIR/${name}_out.txt"

    echo "Running: $name"
    $PROGRAM < "$inputfile" > "$outputfile"
done

echo "Tests complete."