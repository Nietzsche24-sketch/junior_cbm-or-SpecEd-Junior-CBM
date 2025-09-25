#!/usr/bin/env python3
"""
generate_iep.py – Create a printable IEP-style PDF from trend data.
Works with reading_writing/data/assessments_rw.csv.
"""

import csv, argparse
from statistics import mean
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--student", required=True)
    args = p.parse_args()

    csv_path = Path("reading_writing/data/assessments_rw.csv")
    recs = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["student"].strip() == args.student:
                recs.append(r)
    if not recs:
        print(f"No data found for {args.student}")
        return

    # Sort by date
    recs.sort(key=lambda r: r["date"])
    latest = recs[-1]
    enrolled = latest["enrolled_grade"]

    # Compute simple averages by major domain
    def avg(keys):
        return round(mean(float(latest[k]) for k in keys if latest[k]),1)

    reading_avg = avg(["decoding","fluency","literal","inferential","vocabulary","metacognition"])
    writing_avg = avg(["idea_gen","organization","word_choice","conventions","editing"])

    # Build PDF
    out_path = Path(f"reading_writing/reports/{args.student.replace(' ','_')}_IEP.pdf")
    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph(f"Individual Education Plan – {args.student}", styles['Title']))
    elems.append(Spacer(1,12))
    elems.append(Paragraph(f"Enrolled Grade: {enrolled}", styles['Normal']))
    elems.append(Paragraph(f"Reading average: {reading_avg} | Writing average: {writing_avg}", styles['Normal']))
    elems.append(Spacer(1,12))

    # Recent trends table
    headers = ["date","decoding","fluency","literal","inferential","vocabulary","metacognition",
               "idea_gen","organization","word_choice","conventions","editing","notes"]

    data = [headers]
    for r in recs:
        row = [r["date"]] + [r[k] for k in headers[1:-1]] + [r["notes"]]
        data.append(row)
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('FONT',(0,0),(-1,0),'Helvetica-Bold')
    ]))
    elems.append(table)

    elems.append(Spacer(1,12))
    elems.append(Paragraph("Summary & Next Steps:", styles['Heading2']))
    elems.append(Paragraph(
        "Based on the latest diagnostics, key goals are to continue strengthening "
        "inferential comprehension and multi-paragraph writing. Recommended strategies "
        "include explicit text-structure modeling, targeted inference questioning, and "
        "regular guided writing sessions.", styles['Normal']))

    doc.build(elems)
    print(f"[✓] IEP PDF created at {out_path}")

if __name__ == "__main__":
    main()
