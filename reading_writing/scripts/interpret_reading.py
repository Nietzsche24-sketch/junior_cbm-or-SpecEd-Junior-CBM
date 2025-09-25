#!/usr/bin/env python3
import csv, sys, argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import date
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Interpret reading subdomain assessments")
    parser.add_argument("--student", required=True)
    args = parser.parse_args()
    student = args.student.strip()

    csv_file = Path(__file__).resolve().parents[1] / "data" / "assessments.csv"
    report_dir = Path(__file__).resolve().parents[1] / "reports"
    report_dir.mkdir(exist_ok=True)

    records = []
    with csv_file.open() as f:
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            if row[1].strip().lower() == student.lower():
                records.append(row)

    if not records:
        print(f"No records found for {student}")
        return

    # latest record
    r = records[-1]
    # unpack the CSV row
    (d, name, grade_text, dec, flu, comp_lit, comp_inf,
     vocab, meta, notes) = r[0:10] + [""]*(10-len(r))

    # Compute simple averages
    nums = [float(dec), float(flu), float(comp_lit), float(comp_inf),
            float(vocab), float(meta)]
    avg = sum(nums)/len(nums)

    print(f"\n== Reading Profile: {name} ==")
    print(f"Date: {d}")
    print(f"Grade text used: {grade_text}")
    print(f"Domain averages (3–6 scale): {avg:.1f}")
    print(f"Decoding {dec}, Fluency {flu}, Literal {comp_lit}, "
          f"Inferential {comp_inf}, Vocab {vocab}, Metacognition {meta}")
    print(f"Notes: {notes}")

    # --- Create PDF report ---
    pdf_path = report_dir / f"{name.replace(' ', '_')}_reading_report.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 740, f"Reading Profile – {name}")
    c.setFont("Helvetica", 12)
    y = 700
    c.drawString(72, y, f"Date: {d}"); y -= 20
    c.drawString(72, y, f"Grade text used: {grade_text}"); y -= 20
    c.drawString(72, y, f"Overall Avg: {avg:.1f}"); y -= 20
    c.drawString(72, y, f"Decoding: {dec} | Fluency: {flu}"); y -= 20
    c.drawString(72, y, f"Literal: {comp_lit} | Inferential: {comp_inf}"); y -= 20
    c.drawString(72, y, f"Vocabulary: {vocab} | Metacognition: {meta}"); y -= 20
    c.drawString(72, y, f"Notes: {notes}")
    c.showPage()
    c.save()
    print(f"PDF saved to {pdf_path}")

if __name__ == "__main__":
    main()
