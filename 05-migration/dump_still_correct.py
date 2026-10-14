import pandas as pd

p = r"c:\Users\U.lalitha navya sri\Downloads\Logesh files\05-migration\REVIEW_RESOLVED_CORRECT.xlsx"
xl = pd.ExcelFile(p)
print("sheets", xl.sheet_names)
ans = pd.read_excel(p, "ANSWERS")
print("\nANSWERS")
print(ans.to_string(index=False))
still = pd.read_excel(p, "STILL_OPEN_FULL_ROWS")
print("\nSTILL_OPEN rows", len(still))
cols = [
    c
    for c in [
        "status",
        "source_sheet",
        "excel_row",
        "company",
        "combine",
        "year",
        "listing_name_hits",
        "listing_paths",
    ]
    if c in still.columns
]
pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 200)
print(still[cols].to_string(index=False))
print("\n--- unique still companies ---")
print(still["company"].drop_duplicates().to_string(index=False))
print("\nstatus counts in still:")
print(still["status"].value_counts().to_string())
