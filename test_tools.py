import json
from tools import *

def show(title, result):
    print(f"\n=== {title} ===")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

show("inspect", inspect_data())
show("Sales revenue by product", group_stats("products"))
show("December – Regional Breakdown", group_stats("region", filters={"month": "2025-12"}))
show("Monthly Trends", time_trend("month"))
show("Noc.→Dec.", compare_periods("2025-11", "2025-12", "region"))
show("Region name written incorrectly", group_stats("region", filters={"region": "East"}))
show("Visualization", plot("bar", "region", filters={"month": "2025-12"}))