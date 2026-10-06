import pandas as pd

df = pd.read_csv("data/sales.csv", parse_dates=["date"])

print("Missing Values:")
print(df.isna().sum(),"\n")

print("sales revenue for every product:")
print(df.groupby("products")["sales"].sum().sort_values(ascending=False),"\n")

df["month"]  = df["date"].dt.to_period("M")
nov = df[df["month"] == "2025-11"].groupby("region")["sales"].sum()
dec = df[df["month"] == "2025-12"].groupby("region")["sales"].sum()
diff = (dec-nov).sort_values()
print("diffirence between Nov. and Dec.")
print(diff)
print("Overall Diffirence:", diff.sum())