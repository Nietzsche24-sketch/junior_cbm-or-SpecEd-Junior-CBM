#!/usr/bin/env python3
"""
record_reading.py
Logs a reading assessment and auto-credits Mr Youssef Cash.
"""

import csv, datetime, os
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ASSESS = DATA / "assessments.csv"
BANK = DATA / "bank_balances.csv"

def ensure_files():
    for f in [ASSESS, BANK]:
        if not f.exists():
            f.touch()

def current_balance(student):
    ensure_files()
    with open(BANK) as f:
        rows = list(csv.reader(f))
        for r in reversed(rows):
            if r and r[0] == student:
                return float(r[2])
    return 30.0  # default monthly allowance if no record yet

def update_bank(student, amount, reason):
    bal = current_balance(student) + amount
    with open(BANK, "a", newline="") as f:
        csv.writer(f).writerow([student, datetime.date.today(), bal, amount, reason])
    print(f"[Bank] {student} credited {amount:+.2f}, new balance = ${bal:.2f}")

def record_assessment():
    ensure_files()
    student = input("Student name: ").strip()
    grade = input("Grade (3-6): ").strip()
    cluster = input("Cluster (decoding_fluency/comprehension_literal/comprehension_inferential/vocabulary/metacognition_strategies): ").strip()
    score = input("Score or CWPM: ").strip()
    notes = input("Notes: ").strip()

    # log assessment
    with open(ASSESS, "a", newline="") as f:
        csv.writer(f).writerow([datetime.date.today(), student, grade, cluster, score, notes])
    print(f"[Assessment] Saved for {student}.")

    # Auto reward logic
    reward = 0
    if cluster == "decoding_fluency" and score.isdigit() and int(score) >= 120:
        reward += 5
    if cluster.startswith("comprehension") and score.isdigit() and int(score) >= 80:
        reward += 3
    if reward:
        update_bank(student, reward, f"Reading cluster {cluster} target met")

if __name__ == "__main__":
    record_assessment()

