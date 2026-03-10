import os
import json
import re
import httpx
from typing import List, Dict, Any

DO_INFERENCE_ENDPOINT = "https://inference.do-ai.run/v1/chat/completions"

def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

async def _call_inference(messages: List[Dict[str, Any]], max_tokens: int = 512) -> Dict[str, Any]:
    api_key = os.getenv("DIGITALOCEAN_INFERENCE_KEY") or os.getenv("DO_INFERENCE_API_KEY")
    model = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} if api_key else {}
    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(DO_INFERENCE_ENDPOINT, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Assume standard OpenAI response format
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            return json.loads(json_str)
    except Exception as exc:
        # Fallback response
        return {"note": f"AI service temporarily unavailable: {str(exc)}"}

async def generate_ai_tags(title: str, url: str, max_tags: int = 5) -> List[str]:
    """Generate a list of tag suggestions for the given title/url.
    Returns an empty list on failure.
    """
    system_msg = {"role": "system", "content": "You are a helpful assistant that suggests concise, lowercase, hyphen‑free tags for web bookmarks. Return a JSON array of tags only."}
    user_msg = {"role": "user", "content": f"Title: {title}\nURL: {url}\nProvide up to {max_tags} relevant tags."}
    response = await _call_inference([system_msg, user_msg], max_tokens=512)
    if isinstance(response, dict) and "note" in response:
        return []
    if isinstance(response, list):
        return [str(tag).strip() for tag in response][:max_tags]
    # If response is dict with a key like 'tags'
    if isinstance(response, dict):
        tags = response.get("tags") or response.get("suggested_tags") or []
        if isinstance(tags, list):
            return [str(tag).strip() for tag in tags][:max_tags]
    return []
