import pandas as pd

p = r"05-migration\REVIEW_RESOLVED_CORRECT.xlsx"
still = pd.read_excel(p, sheet_name="STILL_OPEN_FULL_ROWS")
print("still", len(still))
cols = ["status", "source_sheet", "excel_row", "company", "combine", "year", "listing_name_hits"]
print(still[cols].to_string())
print("--- status ---")
print(still["status"].value_counts())
print("--- sheets ---")
print(still.groupby("source_sheet").size())
