#!/usr/bin/env python3
"""
interpret_assessment.py
Generates IEP-ready Present Level summaries for Junior-CBM (Ontario Edition).
Usage:
    python3 scripts/interpret_assessment.py --student "Student Name"
"""
import csv, os, argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'assessments.csv')
CURR_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'curriculum')

def calc_level(acc, comp):
    if acc >= 95 and comp >= 80:
        return "Independent"
    elif acc >= 90 and comp >= 60:
        return "Instructional"
    else:
        return "Frustration"

def load_expectations(grade):
    yaml_path = os.path.join(CURR_PATH, f'grade{grade}.yml')
    if not os.path.exists(yaml_path):
        return []
    out = []
    with open(yaml_path) as f:
        for line in f:
            if line.strip().startswith('- '):
                out.append(line.strip()[2:].strip('"'))
    return out

def export_pdf(student, lines):
    pdf_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f"{student.replace(' ', '_')}_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    t = c.beginText(40, 750)
    t.setFont("Helvetica", 11)
    for line in lines:
        t.textLine(line)
    c.drawText(t)
    c.save()
    print(f"PDF saved to {pdf_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--student', required=True)
    args = parser.parse_args()
    target = args.student.lower()

    # Always define records
    records = []

    # Read CSV safely
    if not os.path.exists(DB_PATH):
        print("No assessments.csv found.")
        return

    with open(DB_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['student'].lower() == target:
                records.append(row)

    if not records:
        print(f"No records found for {args.student}")
        return

    # Build output lines
    pdf_lines = [f"Present Level of Achievement: {args.student}"]
    print(f"== Present Level of Achievement: {args.student} ==")

    for r in records:
        total = int(r['total_words'])
        errors = int(r['errors'])
        cwpm = total - errors
        acc = (total - errors) / total * 100
        comp = int(r['comprehension_correct']) / int(r['comprehension_total']) * 100
        level = calc_level(acc, comp)

        pdf_lines += [
            f"Date: {r['date']}",
            f"Text grade used: {r['text_grade']}",
            f"Accuracy: {acc:.1f}% | CWPM: {cwpm} | Comprehension: {comp:.1f}%",
            f"Classification: {level}",
            f"Notes: {r['notes']}",
            "-" * 50
        ]

        print(f"\nDate: {r['date']}")
        print(f"Text grade used: {r['text_grade']}")
        print(f"Accuracy: {acc:.1f}% | CWPM: {cwpm} | Comprehension: {comp:.1f}%")
        print(f"Classification: {level}")
        print(f"Notes: {r['notes']}")

        exp = load_expectations(r['enrolled_grade'])
        if exp:
            print("\nSample Ontario Curriculum Expectations:")
            for e in exp[:3]:
                print(f" - {e}")

    export_pdf(args.student, pdf_lines)

if __name__ == "__main__":
    main()
