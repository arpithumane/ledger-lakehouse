"""Compare an exported quarantine CSV with the planted-defect answer key. Runs on your Mac only.

Usage: python3 stage-2/scripts/check_against_manifest.py <quarantine.csv> <injected_defects.csv>
"""
import csv
import sys


def read_pairs(path, rule_column, key_column):
    with open(path, newline="") as csv_file:
        return {(row[rule_column], row[key_column]) for row in csv.DictReader(csv_file)}


def main():
    caught = read_pairs(sys.argv[1], "rule_id", "record_key")
    planted = read_pairs(sys.argv[2], "defect_type", "key")
    missed, extra = planted - caught, caught - planted
    print(f"Planted: {len(planted)}  Caught: {len(caught)}  Missed: {len(missed)}  Extra: {len(extra)}")
    for rule_id, key in sorted(missed):
        print("MISSED", rule_id, key)
    for rule_id, key in sorted(extra):
        print("EXTRA ", rule_id, key)
    sys.exit(1 if missed or extra else 0)


if __name__ == "__main__":
    main()
