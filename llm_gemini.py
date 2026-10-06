import os
import time
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

from schemas import TOOL_SCHEMAS
from agent_core import SYSTEM_PROMPT

MODELS = ["gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash"]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# The `filters` field in the schema is a free-form object, but Gemini does not accept objects with empty properties;
# therefore, the adaptation layer expands it into three distinct optional fields.
FILTER_PROPS = {
    "month": {"type": "string", "description": "Month, like 2025-12"},
    "region": {"type": "string", "description": "Region, like East"},
    "products": {"type": "string", "description": "Products, like Smartphone"},
}


def _convert_params(params):
    props = {}
    for k, v in params.get("properties", {}).items():
        v = dict(v)
        if v.get("type") == "object":
            v["properties"] = FILTER_PROPS
        props[k] = v
    return {"type": "object", "properties": props, "required": params.get("required", [])}


def _build_tools():
    decls = []
    for s in TOOL_SCHEMAS:
        if s["parameters"].get("properties"):
            decls.append(types.FunctionDeclaration(
                name=s["name"], description=s["description"],
                parameters=_convert_params(s["parameters"])))
        else:  # No parameter tools（inspect_data）
            decls.append(types.FunctionDeclaration(
                name=s["name"], description=s["description"]))
    return [types.Tool(function_declarations=decls)]


CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=_build_tools(),
    temperature=0,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def _clean(v):
    """The integer returned by Gemini might be `1.0`; convert it back to an `int`, otherwise `head(1.0)` will raise an error."""
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    return v


def _generate(contents):
    last_err = None
    for model in MODELS:                      # try every models
        for attempt in range(2):              # try up to 2 times
            t0 = time.time()
            try:
                r = client.models.generate_content(
                    model=model, contents=contents, config=CONFIG)
                print(f"  [{model} response {time.time() - t0:.1f}s]")
                return r,model
            except Exception as e:
                msg = str(e)
                last_err = e
                print(f"  [{model} the {attempt + 1} time fail {time.time() - t0:.1f}s] {msg[:100]}")
                if "429" in msg or "503" in msg:
                    time.sleep(5)             # try later
                    continue
                break                         # other error（like 404/400） try other model
    raise last_err


def llm_step(state):
    # Conversation history is stored in the state; the original `content` returned by the model is preserved 
    # to avoid losing internal signature information.
    if "_contents" not in state:
        state["_contents"] = [types.Content(
            role="user", parts=[types.Part(text=state["question"])])]
        state["_pending"] = 0

    # Package the tool results requested by the model in the previous round and send them back as a user message.
    k = state["_pending"]
    if k:
        parts = [types.Part.from_function_response(
                    name=item["call"]["name"], response={"result": item["result"]})
                 for item in state["tool_results"][-k:]]
        state["_contents"].append(types.Content(role="user", parts=parts))

    resp, used_model = _generate(state["_contents"])
    state.setdefault("models_used", []).append(used_model)
    content = resp.candidates[0].content
    state["_contents"].append(content)

    calls, texts = [], []
    for p in content.parts or []:
        if p.function_call:
            calls.append({"name": p.function_call.name,
                          "args": _clean(dict(p.function_call.args or {}))})
        elif p.text:
            texts.append(p.text)

    state["_pending"] = len(calls)
    return {"text": "".join(texts) or None, "tool_calls": calls}