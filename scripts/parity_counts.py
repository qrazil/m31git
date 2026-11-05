#!/usr/bin/env python3
"""Count the rows of docs/MGIT-PARITY.md by mgit state (done, partial, missing, out of scope)."""
import os
import sys

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "MGIT-PARITY.md")
counts = {"done": 0, "partial": 0, "missing": 0, "out of scope": 0}
for line in open(path):
    if line.startswith("| ") and line.count("|") == 7 and not line.startswith(("| feature", "| state", "| ---")):
        word = line.split("|")[5].strip().split(":")[0].split(" ")[0].split("(")[0]
        key = {"done": "done", "partial": "partial", "missing": "missing", "oos": "out of scope"}.get(word)
        if key:
            counts[key] += 1
total = sum(counts.values())
for key, value in counts.items():
    print("%-13s %d" % (key, value))
print("rows          %d" % total)
sys.exit(0)
