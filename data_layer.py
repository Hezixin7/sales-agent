import pandas as pd

REQUIRED_COLUMNS = ["date", "products","region", "quantity", "sales"]

class DataValidationError(Exception):
    pass



def load_and_validate(path: str="data/sales_frozen.csv"):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise DataValidationError(f"Failed to find this file:{path}")
    
    # check columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols :
        raise DataValidationError(f"Missing Columns:{missing_cols}; current columns:{list(df.columns)}")
    
    # type transformation (--NaT/NaN)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    # missing values report
    missing = {c: int(df[c].isna().sum()) for c in REQUIRED_COLUMNS}
    missing = {c: n for c, n in missing.items() if n > 0}

    report = {
        "rows": len(df),
        "columns": REQUIRED_COLUMNS,
        "missing_values": missing,
        "date_range": [
            df["date"].min().strftime("%Y-%m-%d"),
            df["date"].max().strftime("%Y-%m-%d"),
        ],
        "products": sorted(df["products"].dropna().unique().tolist()),
        "regions": sorted(df["region"].dropna().unique().tolist()),
    }
    return df, report
