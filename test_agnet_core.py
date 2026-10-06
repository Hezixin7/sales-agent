from agent_core import run_agent, save_log

# Mock model: First call to `compare_periods`, second call returns the answer directly.
def fake_llm(state):
    n = len(state["tool_results"])
    if n == 0:
        return {"text": None, "tool_calls": [
            {"name": "compare_periods",
             "args": {"month_a": "2025-11", "month_b": "2025-12"}}]}
    return {"text": "The decline (in the dummy model) is primarily driven by the South and East.", "tool_calls": []}

# Infinite Loop Model: Continuously invoking tools; testing the maximum step count safeguard.
def loop_llm(state):
    return {"text": None, "tool_calls": [{"name": "inspect_data", "args": {}}]}

answer, log = run_agent("Which regions are primarily responsible for the decline in sales this month?", fake_llm)
print(answer)
print("Tool call count:", log["n_tool_calls"])
print("Log file：", save_log(log))

answer, log = run_agent("Test infinite loop", loop_llm)
print("\n", answer, "| Number of calls:", log["n_tool_calls"])