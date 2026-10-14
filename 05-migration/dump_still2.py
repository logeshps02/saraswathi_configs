import pandas as pd

p = r"05-migration\REVIEW_RESOLVED_CORRECT.xlsx"
still = pd.read_excel(p, sheet_name="STILL_OPEN_FULL_ROWS")
print("n", len(still))
print(still[["status", "source_sheet", "excel_row", "company", "combine"]].head(50).to_string())
print("unique companies", still["company"].nunique())
for c in still["company"].drop_duplicates().tolist():
    print("-", c)
