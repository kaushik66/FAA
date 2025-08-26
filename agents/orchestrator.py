# agents/orchestrator.py
import json
from typing import Dict, Any, List
from utils.llm import ask_json
from config import MODEL_BRAIN

ORCHESTRATOR_PROMPT = """
You are the FAA Orchestrator (the brain of the system).
Your job is to plan ONE next action in the fraud investigation.

Allowed tools:
- "sql": run an SQL query on the transactions table.
- "plot": plot the transaction timeline for the given trans_num.
- "stop": finish the investigation when enough evidence is collected.

Transaction table schema (columns you can use):
ssn, cc_num, first, last, gender, street, city, state, zip, lat, long, city_pop, job, dob, acct_num, profile, trans_num, trans_date, trans_time, unix_time, category, amount, merchant, merch_lat, merch_long

⚠️ Important: Do not query or reference "is_fraud". That column exists only for evaluation and is unavailable during investigations. 
Your job is to infer fraud risk based on transaction behavior (amount, merchant, location, time, etc.).

Rules:
- Always output valid JSON.
- Schema must be:
  {
    "tool": "sql" | "plot" | "stop",
    "query": "...",        # for SQL tool, use '?' placeholders for parameters
    "params": [...],       # optional list of parameters for the SQL query; do NOT interpolate variables directly into the query string
    "trans_num": "...",    # for plot tool
    "stop": true/false,
    "notes_for_rga": "short explanation of why you chose this step"
  }
- Never invent column names. Only use what’s in the schema provided by the user.
- If you just did SQL, you may suggest a plot to visualize the transaction.
- Use stop=true only when enough info is gathered for RGA and Detective to decide.
- IMPORTANT: Do NOT directly insert variables or values into the SQL query string. Instead, use '?' placeholders and provide the corresponding values in the 'params' list.
"""

def orchestrator_agent(client, case_id: str, log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Ask the LLM to decide the next action.
    """
    # sanitize log so JSON serialization works
    safe_log = []
    for entry in log[-3:]:
        clean_entry = {}
        for k, v in entry.items():
            if hasattr(v, "to_dict"):  # DataFrame
                clean_entry[k] = {
                    "rows": len(v),
                    "columns": list(v.columns),
                    "sample": v.head(2).to_dict(orient="records")
                }
            else:
                try:
                    json.dumps(v)  # test if serializable
                    clean_entry[k] = v
                except TypeError:
                    clean_entry[k] = str(v)
        safe_log.append(clean_entry)

    user_context = {
        "trans_num": case_id,
        "log": safe_log
    }

    response = ask_json(
        client,
        MODEL_BRAIN,
        ORCHESTRATOR_PROMPT,
        json.dumps(user_context)
    )
    # Ensure 'params' key is present if provided
    if 'params' in response:
        return response
    else:
        return response