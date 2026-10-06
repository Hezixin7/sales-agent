import json
from schemas import TOOL_FUNCS

def run_tool_call(name, arguments):
    if name not in TOOL_FUNCS:
        return {"error": f"unknown tool {name}，options：{list(TOOL_FUNCS)}"}
    try:
        return TOOL_FUNCS[name](**arguments)
    except TypeError as e:          # Incorrect parameter name or missing parameter
        return {"error": f"parameter error：{e}"}
    except Exception as e:
        return {"error": f"Tool excution failed：{e}"}

# Three requests sent by the simulation model
calls = [
    ("compare_periods", {"month_a": "2025-11", "month_b": "2025-12"}),
    ("group_stats", {"group_by": "products", "top_n": 1}),
    ("compare_periods", {"month_a": "2025-11"}),        # miss parameters
    ("drop_table", {}),                                  # Calling a non-existent parameter
]
for name, args in calls:
    print(f"\n>>> {name}({args})")
    print(json.dumps(run_tool_call(name, args), ensure_ascii=False, indent=2)[:400])