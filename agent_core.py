import json
import time
from datetime import datetime
from schemas import TOOL_FUNCS

MAX_STEPS = 8

SYSTEM_PROMPT = """You are a sales data analysis assistant. The data is a sales CSV with the columns: date, products, region, quantity, and sales.

Rules:
1. All numerical figures must be derived from tool outputs; do not perform mental calculations or estimations.
2. You must call `compare_periods` when explaining why sales declined or increased, 
   or identifying the primary sources of these changes.
3. "This month" refers to the most recent month in the dataset, and "last month" refers to the month immediately preceding it.
   Call `inspect_data` first if you are unsure which months are available.
4. If a question requires information not present in the data (e.g., profit, cost, or user count), 
   state clearly that the field is missing; do not fabricate data.
5. The `share_of_decline_pct` value from `compare_periods` applies only to items that declined, 
   representing their proportion of the total decline.
   When answering, also mention which regions or products grew and the extent to which they offset the decline (`total_growth`).
6. Keep answers concise: state the conclusion first, followed by the key figures.
"""


def run_tool_call(name, arguments):
    """Execute a tool call. Returns a dict regardless of any issues; no exceptions are raised."""
    if name not in TOOL_FUNCS:
        return {"error": f"Unknown tool {name}, option：{list(TOOL_FUNCS)}"}
    try:
        return TOOL_FUNCS[name](**arguments)
    except TypeError as e:
        return {"error": f"Parameter error: {e}"}
    except Exception as e:
        return {"error": f"Tool execution failed.: {e}"}


def run_agent(question, llm_step):
    """
    Agent main loop. 
    llm_step(history) -> {"text": str|None, "tool_calls": [{"name":..., "args":{...}}, ...]}
    `history` is an object maintained by `llm_step` itself; here, the responsibility is simply to pass and append to it.
    """
    log = {"question": question, "started": datetime.now().isoformat(), "steps": []}
    state = {"question": question, "tool_results": []}   # to adaptor

    final_text = None
    for step in range(1, MAX_STEPS + 1):
        reply = llm_step(state)

        if not reply["tool_calls"]:
            final_text = reply["text"]
            break

        for call in reply["tool_calls"]:
            t0 = time.time()
            result = run_tool_call(call["name"], call["args"])
            state["tool_results"].append({"call": call, "result": result})
            log["steps"].append({
                "step": step,
                "tool": call["name"],
                "args": call["args"],
                "result_preview": json.dumps(result, ensure_ascii=False)[:300],
                "is_error": "error" in result,
                "seconds": round(time.time() - t0, 3),
            })
    else:
        final_text = "Maximum number of steps reached; final answer not obtained"

    log["answer"] = final_text
    log["models_used"] = state.get("models_used", [])
    log["n_tool_calls"] = len(log["steps"])
    log["charts"] = [s["result_preview"] for s in log["steps"] if s["tool"] == "plot"]
    return final_text, log


def save_log(log, path_prefix="runs/run"):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{path_prefix}_{stamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return path