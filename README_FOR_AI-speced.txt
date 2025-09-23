# Junior-CBM (Ontario Edition) – Tachyon Memory Anchor (spec.Ed)

**Purpose**  
Local, private tool for Special Education teachers to log and interpret
Ontario Language (English) reading assessments in a CBM style.

---

## Folder Layout
junior_cbm/
├── data/
│   ├── curriculum/   # Ontario curriculum YAMLs (grade1.yml done; add grade2-8)
│   ├── norms/        # Percentile or growth norms (future)
│   └── assessments.csv  # All logged probe data
├── scripts/
│   ├── record_assessment.py      # CLI logger
│   └── interpret_assessment.py   # Report + PDF generator
├── reports/       # Auto-generated PDF Present Level reports
└── .venv/         # Python virtual environment (ReportLab installed)

---

## How to Run
1. Activate environment  
   ```bash
   cd ~/speced-tcdsb/junior_cbm
   source .venv/bin/activate
