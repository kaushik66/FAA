import json
from typing import Dict, Any
from config import MODEL_BRAIN
from utils.llm import ask_json

DETECTIVE_PROMPT = (
    "You are the Detective Agent. Given key_evidence, return JSON {verdict: fraud|legit|inconclusive, confidence: 0..1, rationale_short: <string>}"
)


def detective_agent(client, key_evidence: Any) -> Dict[str, Any]:
    # Sanitize key_evidence before serializing to JSON
    sanitized_evidence = key_evidence
    try:
        import pandas as pd
        if isinstance(key_evidence, pd.DataFrame):
            sanitized_evidence = key_evidence.to_dict(orient="records")
        else:
            # Try to serialize, fallback to str if fails
            try:
                json.dumps(key_evidence)
            except (TypeError, OverflowError):
                sanitized_evidence = str(key_evidence)
    except ImportError:
        # If pandas is not installed, fallback to str if not serializable
        try:
            json.dumps(key_evidence)
        except (TypeError, OverflowError):
            sanitized_evidence = str(key_evidence)
    if isinstance(sanitized_evidence, list):
        for record in sanitized_evidence:
            if isinstance(record, dict) and "merchant" in record:
                merchant_value = record["merchant"]
                if isinstance(merchant_value, str) and merchant_value.startswith("fraud_"):
                    record["merchant"] = merchant_value[len("fraud_"):]
    payload = {"key_evidence": sanitized_evidence}
    result = ask_json(client, MODEL_BRAIN, DETECTIVE_PROMPT, json.dumps(payload))
    if (
        result.get("verdict") == "fraud"
        and result.get("confidence", 0) < 0.8
        and result.get("fraud_score", 0) < 2
    ):
        result["verdict"] = "not fraud"
    return result