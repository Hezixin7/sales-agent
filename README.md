# Sales Data Analysis Agent

An LLM agent that answers questions about a sales CSV by calling predefined
Python tools. The model chooses tools and explains results; **all numeric
computation is done by pandas**, not by the model.

## Features
- Fixed-schema CSV loading with column / type / missing-value validation
- 5 tools: `inspect_data`, `group_stats`, `time_trend`, `compare_periods`, `plot`
- Multi-step tool calling with a max-step guard and error feedback to the model
- Model fallback (Gemini) when the primary model is overloaded
- Every run saved as JSON: question, tool calls, results, answer, models used

## Quick start
```bash
git clone https://github.com/<your-name>/sales-agent.git
cd sales-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your Gemini API key in .env
python ask.py "Which product has the highest sales?"
python ask.py "Which regions contributed most to the sales decline this month?"
```

## Example
**Q:** Which regions contributed most to the sales decline this month?

Tool calls: `inspect_data()` → `compare_periods("2025-11", "2025-12", "region")`

**A:** South (-329,312.60, 58.84% of the decline) and East (-230,362.78, 41.16%)
drove the drop, partly offset by growth in North, Northeast and Southwest (+415,823.67).

## Project structure
| File | Purpose |
|---|---|
| `make_data.py` | Generates the synthetic dataset (run once; data is frozen) |
| `data/sales_frozen.csv` | Frozen dataset used for all tests and evaluation |
| `data_layer.py` | CSV loading and validation |
| `tools.py` | The 5 analysis tools |
| `schemas.py` | Tool JSON schemas and dispatch table |
| `agent_core.py` | Agent loop, system prompt, run logging |
| `llm_gemini.py` | Gemini adapter with retry and model fallback |
| `ask.py` | Command-line entry point |

## Evaluation
_To be added._

## Notes
Data is synthetic. Model names change often; edit `MODELS` in `llm_gemini.py`.