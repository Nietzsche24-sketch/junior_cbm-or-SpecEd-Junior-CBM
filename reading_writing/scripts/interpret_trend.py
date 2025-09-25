#!/usr/bin/env python3
import csv, sys, argparse, os
from datetime import datetime
from collections import defaultdict
from statistics import mean
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

DATA_FILE = "reading_writing/data/assessments_rw.csv"
REPORTS_DIR = "reading_writing/reports"

# ---------- Helpers ----------
def load_assessments(student):
    records = []
    with open(DATA_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row["student"].strip().lower() == student.lower():
                records.append(row)
    return records

def numeric(val):
    try: return float(val)
    except: return None

def calc_status(score, enrolled):
    if score - enrolled >= 0.5: return "Exceeding"
    if score - enrolled >= 0:   return "Meeting"
    if score - enrolled >= -0.5:return "Progressing"
    return "Not yet"

def color_for_status(status):
    return {
        "Exceeding": colors.green,
        "Meeting": colors.blue,
        "Progressing": colors.orange,
        "Not yet": colors.red,
    }.get(status, colors.black)

# ---------- PDF builder ----------
def build_pdf(student, enrolled, records):
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    fn = os.path.join(REPORTS_DIR, f"{student.replace(' ','_')}_trend_report.pdf")
    doc = SimpleDocTemplate(fn, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"<b>Reading & Writing Progress – {student}</b>", styles["Title"]))
    story.append(Spacer(1,12))
    story.append(Paragraph(f"Window: {records[0]['date']} → {records[-1]['date']} &nbsp; Enrolled Grade: {enrolled}", styles["Normal"]))
    story.append(Spacer(1,12))

    # Aggregate by subdomain
    subs_read  = ["decoding","fluency","literal","inferential","vocabulary","metacognition"]
    subs_write = ["idea_gen","organization","word_choice","conventions","editing"]
    latest = records[-1]
    tbl_read = [["Reading Subdomain","Latest","Status"]]
    for s in subs_read:
        val = numeric(latest[s])
        tbl_read.append([s.replace("_"," ").title(), val, calc_status(val, enrolled)])
    tbl_write = [["Writing Subdomain","Latest","Status"]]
    for s in subs_write:
        val = numeric(latest[s])
        tbl_write.append([s.replace("_"," ").title(), val, calc_status(val, enrolled)])

    def style_table(data):
        t = Table(data, hAlign="LEFT")
        ts = TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey),
                         ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)])
        # color status cells
        for i,row in enumerate(data[1:], start=1):
            ts.add("TEXTCOLOR",(2,i),(2,i), color_for_status(row[2]))
        t.setStyle(ts)
        return t

    story.append(style_table(tbl_read))
    story.append(Spacer(1,18))
    story.append(style_table(tbl_write))
    story.append(PageBreak())

    # Trend sparkline (text version for now)
    story.append(Paragraph("<b>Trend Summary</b>", styles["Heading2"]))
    for s in subs_read + subs_write:
        vals = [numeric(r[s]) for r in records if numeric(r[s]) is not None]
        if len(vals) > 1:
            direction = "↑" if vals[-1] > vals[0] else "↓" if vals[-1] < vals[0] else "→"
            story.append(Paragraph(f"{s.replace('_',' ').title()}: {vals[0]} → {vals[-1]} {direction}", styles["Normal"]))

    doc.build(story)
    print(f"[✓] Trend PDF saved to {fn}")

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student", required=True)
    args = ap.parse_args()

    recs = sorted(load_assessments(args.student), key=lambda r: r["date"])
    if not recs:
        print("No records for", args.student)
        sys.exit(0)

    enrolled = numeric(recs[-1]["enrolled_grade"])
    build_pdf(args.student, enrolled, recs)

if __name__ == "__main__":
    main()
