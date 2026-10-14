from pathlib import Path

import pandas as pd

root = Path(r"c:\Users\U.lalitha navya sri\Downloads\Logesh files")
review = root / "NOT FOUND - REVIEW - ALL COMPLETED.xlsx"
todo = root / "05-migration" / "MISSING_AND_ISSUES_TO_DO.xlsx"

for name in ["REMAINING_MISSING", "REVIEW_STILL_OPEN"]:
    df = pd.read_excel(review, sheet_name=name, dtype=str).fillna("")
    print("====", name, len(df), list(df.columns))
    print(df.head(2).to_string())
    if name == "REMAINING_MISSING":
        print("still_needed", df["still_needed"].value_counts().to_string())
    if name == "REVIEW_STILL_OPEN":
        print("category", df["category"].value_counts().to_string())

td = pd.read_excel(todo, sheet_name="TO_DO", dtype=str).fillna("")
print("==== TO_DO", len(td), list(td.columns))
print(td["to_do"].value_counts().to_string())
