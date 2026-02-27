import os
import difflib

expected_dir = "test_IO/expected/out"
results_dir = "test_IO/results"

rows = []

for expected in os.listdir(expected_dir):
    if not expected.endswith("_out.txt"):
        continue

    name = expected.replace("_out.txt", "")
    expected_path = os.path.join(expected_dir, expected)
    result_path = os.path.join(results_dir, f"{name}_out.txt")

    try:
        with open(expected_path) as f:
            exp = f.readlines()
    except FileNotFoundError:
        exp = []

    try:
        with open(result_path) as f:
            out = f.readlines()
    except FileNotFoundError:
        out = []

    if exp != out:
        diff = difflib.unified_diff(exp, out, lineterm="")
        rows.append((name, "FAIL", "".join(diff)))
    else:
        rows.append((name, "PASS", ""))

# generate markdown table
print("| Test | Result | Diff |")
print("|------|--------|------|")

fail_count = 0
total_count = 0

for name, result, diff in rows:
    diff_cell = "\n```\n" + diff + "\n```" if diff else ""
    total_count += 1

    if result == "FAIL":
        fail_count += 1
        print(f"| {name} | {result} | {diff_cell}")
    else:
        print(f"| {name} | {result} |")

print(f"\n {total_count - fail_count} / {total_count} tests passed \n {fail_count} tests failed")
