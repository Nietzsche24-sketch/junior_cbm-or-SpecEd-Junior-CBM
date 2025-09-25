import csv, os, math
from datetime import datetime
from statistics import mean
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

DATA   = "reading_writing/data/assessments_rw.csv"
TARGET = "reading_writing/data/iep_targets.csv"
OUTDIR = "reading_writing/reports"

READING = [
    "decoding","phonemic_awareness","phonics",
    "fluency","prosody",
    "literal","inferential","critical_reading","text_structure","author_purpose",
    "vocabulary","morphology",
    "metacognition","self_monitoring","fix_up_strategies"
]

WRITING = [
    "idea_gen","prewriting","organization","sentence_fluency","text_structure_genre",
    "word_choice","grammar_usage","spelling","conventions",
    "editing","feedback_integration","presentation_layout"
]

def num(x):
    try:
        return float(x)
    except:
        return None

def read_rows(student):
    rows = []
    with open(DATA,newline="") as f:
        for r in csv.DictReader(f):
            if r["student"].strip()==student:
                r["_date"]=datetime.strptime(r["date"],"%Y-%m-%d")
                r["_enrolled"]=num(r["enrolled_grade"])
                rows.append(r)
    rows.sort(key=lambda r:r["_date"])
    return rows

def read_targets(student):
    t = {}
    if not os.path.exists(TARGET): return t
    with open(TARGET,newline="") as f:
        for r in csv.DictReader(f):
            if r["student"].strip()==student:
                t[r["domain"].strip()] = num(r["target"])
    return t

def status(latest, target):
    # Atlas mapping vs IEP target
    if latest is None or target is None: return "—"
    if latest >= target + 0.5: return "Exceeding"
    if latest >= target + 0.0: return "Meeting"
    if latest >= target - 0.5: return "Progressing"
    return "Not yet"

def latest_for(rows, key):
    vals = [num(r.get(key)) for r in rows if r.get(key,"")!=""]
    return None if not vals else vals[-1]

def first_for(rows, key):
    vals = [num(r.get(key)) for r in rows if r.get(key,"")!=""]
    return None if not vals else vals[0]

def arrow(first, last):
    if first is None or last is None: return "→"
    delta = last-first
    if delta > 0.15: return "↑"
    if delta < -0.15: return "↓"
    return "→"

def fmt(x):
    return "—" if x is None else f"{x:.1f}"

def build(student):
    rows = read_rows(student)
    if not rows: raise SystemExit("No rows for student.")
    targets = read_targets(student)
    window = f"{rows[0]['date']} → {rows[-1]['date']}"
    enrolled = rows[-1]["_enrolled"]

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]; h2 = styles["Heading2"]; body = styles["BodyText"]

    doc = SimpleDocTemplate(os.path.join(OUTDIR,f"{student.replace(' ','_')}_atlas_trend.pdf"),
                            pagesize=letter, topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36)
    story = []
    story += [Paragraph(f"Reading & Writing Progress — {student}", h1),
              Paragraph(f"Window: {window} &nbsp;&nbsp;•&nbsp;&nbsp; Enrolled Grade: {enrolled:.1f}", body),
              Spacer(1,12)]

    def build_table(domains, title):
        data = [["Subdomain","Latest","Target","Status"]]
        for d in domains:
            last  = latest_for(rows,d)
            targ  = targets.get(d, enrolled)  # fallback to enrolled if no IEP target present
            data += [[d.replace('_',' ').title(), fmt(last), fmt(targ), status(last,targ)]]
        tbl = Table(data, colWidths=[180,60,60,110])
        tbl.setStyle(TableStyle([
            ("FONT",(0,0),(-1,0),"Helvetica-Bold",10),
            ("ALIGN",(1,1),(-2,-1),"RIGHT"),
            ("GRID",(0,0),(-1,-1),0.3,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
            ("TEXTCOLOR",(3,1),(3,-1),colors.black),
        ]))
        story.extend([Paragraph(title,h2), tbl, Spacer(1,16)])

    build_table(READING, "Reading (vs IEP targets)")
    build_table(WRITING, "Writing (vs IEP targets)")

    # Trend summary
    story += [Paragraph("Trend Summary", h2)]
    lines=[]
    for d in READING+WRITING:
        first=first_for(rows,d); last=latest_for(rows,d)
        lines.append(f"{d.replace('_',' ').title()}: {fmt(first)} → {fmt(last)} {arrow(first,last)}")
    for ln in lines:
        story.append(Paragraph(ln, body))
    doc.build(story)
    return doc.filename

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--student", required=True)
    args=ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    path = build(args.student)
    print(f"[✓] Atlas PDF saved to {path}")
