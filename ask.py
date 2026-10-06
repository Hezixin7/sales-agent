import sys
from agent_core import run_agent, save_log
from llm_gemini import llm_step

question = " ".join(sys.argv[1:]) or "Which product has the highest sales?"
answer, log = run_agent(question, llm_step)

print("\n=== Tool Call Logs ===")
for s in log["steps"]:
    flag = "❌" if s["is_error"] else "✅"
    print(f'{flag} step{s["step"]} {s["tool"]}({s["args"]})')
print("\n=== Answer ===")
print(answer)
print("\nLog:", save_log(log))