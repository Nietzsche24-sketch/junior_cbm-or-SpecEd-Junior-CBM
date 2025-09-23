#!/usr/bin/env python3
"""
record_assessment.py
Quick CLI logger for Junior-CBM (Ontario Edition)

Usage:
    python3 record_assessment.py
Then follow the prompts.
"""
import csv, os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), '..',
                       'data', 'assessments.csv')

def ensure_header():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date','student','enrolled_grade','text_grade',
                'total_words','errors','cwpm','comprehension_correct',
                'comprehension_total','notes'
            ])

def main():
    ensure_header()
    today = date.today().isoformat()
    print("== Junior-CBM Assessment Logger ==")
    student = input("Student name: ").strip()
    enrolled_grade = input("Enrolled grade: ").strip()
    text_grade = input("Grade level of text used: ").strip()
    total_words = int(input("Total words in passage: ").strip())
    errors = int(input("Number of errors: ").strip())
    cwpm = total_words - errors
    comp_correct = input("Comprehension correct (#): ").strip()
    comp_total   = input("Comprehension total (#): ").strip()
    notes = input("Notes (optional): ").strip()

    with open(DB_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            today, student, enrolled_grade, text_grade,
            total_words, errors, cwpm, comp_correct,
            comp_total, notes
        ])

    print(f"Saved assessment for {student} on {today} with {cwpm} CWPM.")

if __name__ == "__main__":
    main()
