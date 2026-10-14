import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "BACKUP WORK - FINAL SHEET - WITH PATHS (12).xlsx"
uf = pd.read_excel(FINAL, sheet_name="UPLOADED FORMS - COMPANY NAME", dtype=object, nrows=3)
print("UF COLS", list(uf.columns))
print(uf.head(2).to_string())
cw = pd.read_excel(FINAL, sheet_name="COMPANY WISE", dtype=object, nrows=2)
print("CW COLS", list(cw.columns))
