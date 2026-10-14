import pandas as pd

p = r"c:\Users\U.lalitha navya sri\Downloads\Logesh files\05-migration\REVIEW_RESOLVED_CORRECT.xlsx"
still = pd.read_excel(p, "STILL_OPEN_FULL_ROWS")
rev = pd.read_excel(p, "REVIEW_STYLE_RESOLVED")
print("review_style_rows", len(rev))
print("resolved", int(rev["status"].astype(str).str.startswith("RESOLVED").sum()))
print("still_open", len(still))
print()
print("STILL_NO_TRUE:")
s = still[still["status"] == "STILL_NO_TRUE"]
for _, r in s.iterrows():
    print(f"  {r['source_sheet']}|{r['excel_row']}|{r['company']}|{r['combine']}|{r['year']}")
print()
print("NO_TRUE_BUT_NAME_IN_FILE_LIST:")
s = still[still["status"] == "NO_TRUE_BUT_NAME_IN_FILE_LIST"]
for _, r in s.iterrows():
    paths = str(r.get("listing_paths") or "").split(" ; ")
    print(f"  {r['source_sheet']}|{r['excel_row']}|{r['company']}|{r['combine']}|hits={r['listing_name_hits']}")
    print(f"    first={paths[0][:140]}")
print()
print("unique still companies by status:")
print(still.groupby("status")["company"].nunique().to_string())
print()
print("unique companies still no true:")
print("\n".join(sorted(still.loc[still["status"] == "STILL_NO_TRUE", "company"].dropna().unique())))
print()
print("unique companies listing-only:")
print("\n".join(sorted(still.loc[still["status"] == "NO_TRUE_BUT_NAME_IN_FILE_LIST", "company"].dropna().unique())))
