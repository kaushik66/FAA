import json
from typing import Dict, Any
from config import MODEL_BRAIN
from utils.llm import ask_json

RGA_PROMPT = (
    "You are the Report-Generating Agent (RGA). Given the full investigation log, write: (1) a concise narrative report,\n"
    "(2) a distilled key_evidence JSON array where each item has {signal, impact, why}. Respond with a JSON object:\n"
    "{\"report\": <string>, \"key_evidence\": [ {\"signal\":..., \"impact\":..., \"why\":...}, ... ]}\n"
    "If any SQL queries are included in your reasoning or logs, they must be written using parameterized syntax with `?` placeholders\n"
    "and a separate `params` array, not direct string interpolation."
)


def rga_agent(client, investigation_log: Any):
    safe_log = []
    for entry in investigation_log:
        clean_entry = {}
        for k, v in entry.items():
            if isinstance(v, dict) and "query" in v and "params" in v:
                # Assume this is a SQL query with parameters
                clean_entry[k] = {
                    "query": v["query"],
                    "params": v["params"]
                }
            elif hasattr(v, "to_dict"):  # DataFrame
                clean_entry[k] = {
                    "rows": len(v),
                    "columns": list(v.columns),
                    "sample": v.head(2).to_dict(orient="records")
                }
            else:
                try:
                    json.dumps(v)
                    clean_entry[k] = v
                except TypeError:
                    clean_entry[k] = str(v)
        safe_log.append(clean_entry)

    payload = {"log": safe_log}
    result = ask_json(client, MODEL_BRAIN, RGA_PROMPT, json.dumps(payload))
    return result["report"], result["key_evidence"]