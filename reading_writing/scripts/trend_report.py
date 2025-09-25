#!/usr/bin/env python3
import csv
from datetime import datetime
from pathlib import Path
from statistics import mean

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "assessments_rw.csv"
OUTDIR = BASE / "reports"
OUTDIR.mkdir(exist_ok=True)

READING_KEYS = ["decoding","fluency","literal","inferential","vocabulary","metacognition"]
WRITING_KEYS = ["idea_gen","organization","word_choice","conventions","editing"]

def parse_csv(student):
    rows = []
    if not DATA.exists():
        return rows
    with DATA.open() as f:
        reader = csv.reader(f)
        header = next(reader, [])
        # Map headers to indices
        h = {k:i for i,k in enumerate(header)}
        for r in reader:
            if not r or len(r) < 16: 
                continue
            if r[h["student"]].strip().lower() != student.lower():
                continue
            try:
                d = datetime.strptime(r[h["date"]], "%Y-%m-%d").date()
            except Exception:
                continue
            rec = dict(
                date=d,
                student=r[h["student"]].strip(),
                enrolled=float(r[h["enrolled_grade"]]),
                grade_text=float(r[h["grade_text_used"]]),
                notes=r[h["notes"]].strip()
            )
            for key in READING_KEYS + WRITING_KEYS:
                rec[key] = float(r[h[key]]) if r[h[key]] else None
            rows.append(rec)
    rows.sort(key=lambda x: x["date"])
    return rows

def trend_arrow(values):
    pts = [v for v in values if v is not None]
    if len(pts) < 2: 
        return "→"
    # last-delta heuristic
    delta = pts[-1] - pts[-2]
    if delta > 0.09: return "↑"
    if delta < -0.09: return "↓"
    return "→"

def status_label(value, target):
    if value is None:
        return "—"
    # target is enrolled grade (e.g., 5.0)
    if value >= target + 0.5:  return "Exceeding"
    if value >= target:        return "Meeting"
    if value >= target - 0.5:  return "Progressing"
    return "Not yet"

def draw_sparkline(c, x, y, w, h, series, band=(3.0,6.0)):
    # Background band
    c.setStrokeColor(colors.lightgrey)
    c.rect(x, y, w, h, stroke=1, fill=0)
    vals = [v for v in series if v is not None]
    if len(vals) == 0:
        return
    vmin, vmax = band
    # map points to box
    pts = []
    n = len(series)
    for i, v in enumerate(series):
        if v is None: 
            continue
        px = x + (i/(max(n-1,1))) * w
        py = y + ((v - vmin)/(vmax - vmin)) * h
        pts.append((px, py))
    # draw line
    if len(pts) >= 2:
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.lines([(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1]) for i in range(len(pts)-1)])
    # last point dot
    lx, ly = pts[-1]
    c.circle(lx, ly, 1.8, stroke=1, fill=1)

def build_pdf(student, rows):
    if not rows:
        print(f"No data for {student}")
        return
    pdf = OUTDIR / f"{student.replace(' ','_')}_trend.pdf"
    c = canvas.Canvas(str(pdf), pagesize=letter)
    W, H = letter

    # HEADER
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, H-60, f"Reading & Writing Progress – {student}")
    c.setFont("Helvetica", 11)
    start, end = rows[0]["date"], rows[-1]["date"]
    c.drawString(72, H-80, f"Window: {start} → {end}   •   Points: {len(rows)}")
    enrolled = rows[-1]["enrolled"]
    c.drawString(72, H-96, f"Enrolled Grade: {enrolled:.1f}   (Targets compare to enrolled grade)")

    # LATEST TABLES
    y = H-130
    c.setFont("Helvetica-Bold", 12); c.drawString(72, y, "Reading (latest)"); y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Subdomain");   c.drawString(240, y, "Latest"); c.drawString(300, y, "Status"); c.drawString(380, y, "Trend"); y -= 12
    c.line(72, y, 500, y); y -= 8

    latest = rows[-1]
    # build series per key
    series = {k: [r[k] for r in rows] for k in READING_KEYS + WRITING_KEYS}

    for key in READING_KEYS:
        val = latest[key]
        stat = status_label(val, enrolled)
        arr = trend_arrow(series[key])
        label = {
            "decoding":"Decoding", "fluency":"Fluency", "literal":"Comprehension (Literal)",
            "inferential":"Comprehension (Inferential)", "vocabulary":"Vocabulary",
            "metacognition":"Metacognition"
        }[key]
        c.drawString(72, y, label)
        c.drawString(240, y, f"{val:.1f}" if val is not None else "—")
        c.drawString(300, y, stat)
        c.drawString(380, y, arr)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12); c.drawString(72, y, "Writing (latest)"); y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(72, y, "Subdomain");   c.drawString(240, y, "Latest"); c.drawString(300, y, "Status"); c.drawString(380, y, "Trend"); y -= 12
    c.line(72, y, 500, y); y -= 8

    for key in WRITING_KEYS:
        val = latest[key]
        stat = status_label(val, enrolled)
        arr = trend_arrow(series[key])
        label = {
            "idea_gen":"Ideas / Planning", "organization":"Organization",
            "word_choice":"Word Choice / Voice", "conventions":"Conventions",
            "editing":"Revising / Editing"
        }[key]
        c.drawString(72, y, label)
        c.drawString(240, y, f"{val:.1f}" if val is not None else "—")
        c.drawString(300, y, stat)
        c.drawString(380, y, arr)
        y -= 14

    # SPARKLINES (Reading)
    y -= 12
    c.setFont("Helvetica-Bold", 12); c.drawString(72, y, "Reading Trend Sparklines (3.0–6.0 band)"); y -= 8
    c.setFont("Helvetica", 9)
    box_w, box_h = 140, 40
    x0, y0 = 72, y - box_h - 4
    for i, key in enumerate(READING_KEYS):
        if i and i % 3 == 0:
            x0 = 72
            y0 -= (box_h + 28)
        label = {
            "decoding":"Decoding", "fluency":"Fluency", "literal":"Literal",
            "inferential":"Inferential", "vocabulary":"Vocabulary", "metacognition":"Metacognition"
        }[key]
        c.drawString(x0, y0 + box_h + 12, label)
        draw_sparkline(c, x0, y0, box_w, box_h, series[key])
        x0 += (box_w + 28)

    # SPARKLINES (Writing)
    y0 -= (box_h + 40)
    c.setFont("Helvetica-Bold", 12); c.drawString(72, y0 + box_h + 20, "Writing Trend Sparklines (3.0–6.0 band)")
    x0 = 72
    for i, key in enumerate(WRITING_KEYS):
        label = {
            "idea_gen":"Ideas", "organization":"Org", "word_choice":"Words",
            "conventions":"Conv", "editing":"Edit"
        }[key]
        c.setFont("Helvetica", 9); c.drawString(x0, y0 + box_h + 12, label)
        draw_sparkline(c, x0, y0, box_w, box_h, series[key])
        x0 += (box_w + 28)

    # FOOTER
    c.setFont("Helvetica", 8)
    c.drawString(72, 36, "Status vs Enrolled Grade: Exceeding (>= +0.5) • Meeting (>= 0) • Progressing (>= -0.5) • Not yet (< -0.5)")
    c.drawString(72, 24, "Reading & Writing only • No media/oral strands • Generated by Junior-CBM Reading/Writing Engine")

    c.showPage()
    c.save()
    print(f"PDF saved to {pdf}")
    return pdf

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--student", required=True)
    args = p.parse_args()
    rows = parse_csv(args.student)
    build_pdf(args.student, rows)

if __name__ == "__main__":
    main()
