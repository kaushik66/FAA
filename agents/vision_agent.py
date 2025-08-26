import json
import base64
from typing import Any, Dict
from config import MODEL_VISION
from utils.llm import ask_json
import os

VISION_PROMPT = (
    "You are the Vision Agent. Analyze the attached plot image for anomalies, suspicious patterns, "
    "clusters, or spikes in transaction activity. Return JSON with keys: "
    "{summary: <string>, anomalies: [list of strings]}"
)

def vision_agent(client, plot_path: str) -> Dict[str, Any]:
    if not os.path.exists(plot_path):
        raise FileNotFoundError(f"The specified plot_path does not exist: {plot_path}")
    try:
        with open(plot_path, "rb") as f:
            img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read and encode the image file: {e}")

    # Wrap into OpenAI vision input
    result = client.chat.completions.create(
        model=MODEL_VISION,
        messages=[
            {
                "role": "system",
                "content": VISION_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this plot for fraud evidence:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ],
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(result.choices[0].message.content)