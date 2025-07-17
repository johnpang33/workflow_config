import pandas as pd

# Load both CSVs
df1 = pd.read_csv("output.csv")
df2 = pd.read_csv("output1.csv")

# Check if DataFrames are exactly equal
if df1.equals(df2):
    print("✅ The CSV files are exactly the same.")
else:
    print("❌ The CSV files are different.")