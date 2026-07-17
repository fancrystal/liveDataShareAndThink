import json
from typing import Any

import httpx


class DeepSeekPostPackager:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.deepseek.com", client: httpx.Client | None = None) -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    def create(self, topic: str, angle: str, evidence: list[str]) -> dict[str, Any]:
        request = {"topic": topic, "angle": angle, "evidence": evidence, "required_json": ["title", "caption", "tags", "pages"]}
        try:
            response = self.client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Return JSON only. Create original Xiaohongshu post. pages must contain exactly 5 items with heading and body. Do not claim unsupported medical outcomes."}, {"role": "user", "content": json.dumps(request, ensure_ascii=False)}]})
            response.raise_for_status()
            result = json.loads(response.json()["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise RuntimeError("DeepSeek post package request failed") from error
        if not isinstance(result.get("title"), str) or not isinstance(result.get("caption"), str) or not isinstance(result.get("tags"), list) or not isinstance(result.get("pages"), list) or len(result["pages"]) != 5:
            raise RuntimeError("DeepSeek post package response is invalid")
        return result
