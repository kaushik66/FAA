import json
from typing import Dict, Any, Optional
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def parse_llm_json(text: str) -> dict:
    """
    Try to parse LLM output into JSON.
    If parsing fails, wrap the text in a dict under 'raw'.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fallback: try to fix common JSON formatting issues
        cleaned = text.strip()
        # Sometimes LLMs wrap JSON in code fences ```json ... ```
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return {"raw": text}


def ask_json(client: OpenAI, model: str, system_prompt: str, user_content: str,
             temperature: float = 0) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=temperature,
    )
    text = resp.choices[0].message.content.strip()
    # Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        # Fallback: extract the first JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise RuntimeError(f"Model did not return valid JSON. Got:\n{text}")