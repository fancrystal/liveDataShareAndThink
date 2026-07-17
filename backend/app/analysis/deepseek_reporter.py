import json
from typing import Any

import httpx


class DeepSeekHotReporter:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.deepseek.com", client: httpx.Client | None = None) -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    def analyze(self, topic: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        prompt = {"topic": topic, "candidates": candidates, "required_json": ["today_summary", "hot_reasons", "replication_checklist", "disclosure"]}
        try:
            response = self.client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "只返回 JSON。仅分析提供的公开素材，today_summary、hot_reasons、replication_checklist 和 disclosure 的所有内容必须使用简体中文，不得使用英文或英文缩写；未知发布时间必须明确说明。"}, {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}]})
            response.raise_for_status()
            result = json.loads(response.json()["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise RuntimeError("DeepSeek hot report request failed") from error
        if not all(isinstance(result.get(key), (str, list)) for key in ("today_summary", "hot_reasons", "replication_checklist", "disclosure")):
            raise RuntimeError("DeepSeek hot report response is invalid")
        return result
