import pandas as pd

p = r"05-migration\REVIEW_RESOLVED_CORRECT.xlsx"
still = pd.read_excel(p, sheet_name="STILL_OPEN_FULL_ROWS")
true = pd.read_excel(p, sheet_name="ALL_TRUE_PATH_ROWS")
print("still unique companies", still["company"].nunique())
print("true unique companies", true["company"].nunique())
print("\nSTILL COMPANIES:")
for c in still["company"].fillna("").drop_duplicates():
    print("STILL|", c)
print("\nTRUE COMPANIES:")
for c in true["company"].fillna("").drop_duplicates():
    print("TRUE|", c)
