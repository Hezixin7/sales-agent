import matplotlib
matplotlib.use("Agg") # no pop-ups, save file only
import matplotlib.pyplot as plt
import pandas as pd

from data_layer import load_and_validate

DF, REPORT = load_and_validate()
DF["month"] = DF["date"].dt.to_period("M").astype(str)

DIMENSIONS = ["products", "region", "month"]
VALID_VALUES = {
    "products": REPORT["products"],
    "region": REPORT["regions"],
}


AGG_FUNCS ={"sum": "sum", "mean":"mean", "count":"count"}
METRICS =["sales", "quantity"]


def _apply_filters(df, filters):
    if not filters:
        return df, None
    for col, val in filters.items():
        if col not in DIMENSIONS:
            return None, {"error": f"can not filtered by{col}, options:{DIMENSIONS}" }
        if col in VALID_VALUES and val not in VALID_VALUES[col]:
            return None, {"error":f"No {col}, options{VALID_VALUES[col]}"}
        df = df[df[col] == val]
    return df, None


def inspect_data():
    return REPORT


def group_stats(group_by, agg="sum", metric="sales", top_n=10, filters=None):
    if group_by not in DIMENSIONS:
        return {"error": f"Group_by has to be {DIMENSIONS}"}
    if agg not in AGG_FUNCS:
        return {"error": f"agg has to be {AGG_FUNCS}"}
    if metric not in METRICS:
        return {"error": f"metric has to be  {METRICS}"}
    
    df, err = _apply_filters(DF, filters)
    if err:
        return err
    result = (df.groupby(group_by)[metric].agg(AGG_FUNCS[agg]).sort_values(ascending=False).head(top_n).round(2))

    return {"group_by": group_by, "agg": agg, "metric": metric, "result": result.to_dict()}


def time_trend(freq="month", filters=None):
    """sales revenue time trend freq:day/week/month"""
    freq_map = {"day": "D", "week": "W", "month": "MS"}
    if freq not in freq_map:
        return {"error": "freq must be day, week or month"}
    df, err = _apply_filters(DF, filters)
    if err:
        return err
    s = df.set_index("date")["sales"].resample(freq_map[freq]).sum().round(2)
    s.index = s.index.strftime("%Y-%m-%d")

    return {"freq":freq, "series":s.to_dict()}


def compare_periods(month_a, month_b, group_by="region"):
    """Compare two months (b - a) and return the amount of change and the contribution percentage, broken down by dimension."""
    if group_by not in ["products", "region"]:
        return {"error": "group_by has to be products or region."}
    months = sorted(DF["month"].unique())
    for m in (month_a, month_b):
        if m not in months:
            return {"error": f"month '{m}' not exits, options:{months}"}
    a = DF[DF["month"] == month_a].groupby(group_by)["sales"].sum()
    b = DF[DF["month"] == month_b].groupby(group_by)["sales"].sum()
    diff = (b-a).fillna(0)
    total = diff.sum()
    total_decline = diff[diff < 0].sum()   # Sum of all negative items (negative values)
    total_growth = diff[diff > 0].sum()    # The sum of all rising terms (positive number)
    out = pd.DataFrame({
        "period_a": a, "period_b": b, "change": diff, "pct_change": (diff / a * 100),
        "share_of_decline_pct": (diff / total_decline * 100).where(diff<0),}).round(2).sort_values("change")
    out = out.astype(object).where(out.notna(), None)
    return {"month_a": month_a,
            "month_b": month_b, 
            "group_by": group_by,
            "total_change": round(float(total), 2),
            "total_decline": round(float(total_decline), 2),
            "total_growth": round(float(total_growth), 2),
            "rows": out.reset_index().to_dict(orient="records")}

def plot(kind, x, y="sales", filters=None, filename=None):
    """visulization。kind: line / bar;x: month / region / products"""
    if kind not in ("line", "bar"):
        return {"error": "kind has to be line or bar"}
    if x not in DIMENSIONS:
        return {"error": f"x has to be {DIMENSIONS}"}
    if y not in METRICS:
        return {"error": f"y has to be {METRICS}"}
    df, err = _apply_filters(DF, filters)
    if err:
        return err
    data = df.groupby(x)[y].sum()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # data.plot(kind=kind, ax=ax, marker="o" if kind == "line" else None)
    if kind == "line":
        data.plot(kind="line", ax=ax, marker="o")
    else:
        data.plot(kind="bar", ax=ax)
    ax.set_title(f"{y} by {x}" + (f" {filters}" if filters else ""))
    ax.set_ylabel(y)
    fig.tight_layout()
    path = f"outputs/{filename or f'{kind}_{x}_{y}'}.png"
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return {"saved_to": path, "data": data.round(2).to_dict()}