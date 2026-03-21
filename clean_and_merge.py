import pandas as pd

# Load all 3 files
df2023 = pd.read_csv("hbtu_all_rounds_orcr_2023.csv")
df2024 = pd.read_csv("hbtu_all_rounds_orcr_2024.csv")
df2025 = pd.read_csv("hbtu_all_rounds_orcr_2025.csv")

# Clean column names (remove spaces + special arrows)
for df in [df2023, df2024, df2025]:
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("▲▼", "", regex=False)
        .str.strip()
    )

# Add year column
df2023["year"] = 2023
df2024["year"] = 2024
df2025["year"] = 2025

# Combine
df = pd.concat([df2023, df2024, df2025], ignore_index=True)

# Standardize column names
df = df.rename(columns={
    "Program": "branch",
    "Category": "category",
    "Quota": "quota",
    "Opening Rank": "opening_rank",
    "Closing Rank": "closing_rank",
    "Round_Name": "round"
})

# Convert ranks to numeric
df["opening_rank"] = pd.to_numeric(df["opening_rank"], errors="coerce").round(0).astype("Int64")
df["closing_rank"] = pd.to_numeric(df["closing_rank"], errors="coerce").round(0).astype("Int64")
# Remove rows without closing rank
df = df.dropna(subset=["closing_rank"])

# Keep only required columns for database
df = df[[
    "year",
    "round",
    "branch",
    "category",
    "quota",
    "opening_rank",
    "closing_rank"
]]

# Clean spaces
df["branch"] = df["branch"].str.strip()
df["category"] = df["category"].str.strip()
df["quota"] = df["quota"].str.strip()
df["round"] = df["round"].str.strip()

# Save clean file
df.to_csv("hbtu_combined_cleaned.csv", index=False)

print("Done.")
print("Total rows:", len(df))
print(df.head())