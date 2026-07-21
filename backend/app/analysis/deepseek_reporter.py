import json
import re
from typing import Any

import httpx


class DeepSeekHotReporter:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.deepseek.com", client: httpx.Client | None = None) -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    def analyze(self, topic: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        prompt = {
            "topic": topic,
            "candidates": candidates,
            "required_json": {
                "today_summary": "字符串",
                "hot_reasons": ["字符串", "字符串"],
                "replication_checklist": ["字符串", "字符串"],
                "disclosure": "字符串",
            },
        }
        messages = [
            {"role": "system", "content": "只返回 JSON。仅分析提供的公开素材。today_summary 和 disclosure 必须是字符串；hot_reasons 与 replication_checklist 必须是字符串数组，不能写成一个长字符串。所有内容必须使用简体中文，不得使用英文或英文缩写；未知发布时间必须明确说明；不得将未提供的事实当作证据。"},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ]
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "response_format": {"type": "json_object"}, "messages": messages},
                )
                response.raise_for_status()
                result = self._normalize(json.loads(response.json()["choices"][0]["message"]["content"]))
                if self._is_valid(result):
                    return result
                last_error = RuntimeError("DeepSeek hot report response is invalid")
            except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
                last_error = error
            if attempt == 0:
                messages.append({"role": "user", "content": "上一次结果不可用。请严格重写为不含英文的完整中文 JSON；hot_reasons 和 replication_checklist 必须分别是字符串数组，不要附加解释。"})
        raise RuntimeError("DeepSeek hot report request failed") from last_error

    @staticmethod
    def _normalize(result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        normalized = dict(result)
        for key in ("hot_reasons", "replication_checklist"):
            value = normalized.get(key)
            if isinstance(value, str):
                normalized[key] = [
                    re.sub(r"^\s*\d+[.、]？?\s*", "", item).strip()
                    for item in re.split(r"[；;\n]", value)
                    if item.strip()
                ]
        return normalized

    @staticmethod
    def _is_valid(result: Any) -> bool:
        required = ("today_summary", "hot_reasons", "replication_checklist", "disclosure")
        if not isinstance(result, dict) or not all(isinstance(result.get(key), str) for key in ("today_summary", "disclosure")):
            return False
        if not all(isinstance(result.get(key), list) and all(isinstance(item, str) for item in result[key]) for key in ("hot_reasons", "replication_checklist")):
            return False
        text = [result["today_summary"], result["disclosure"], *result["hot_reasons"], *result["replication_checklist"]]
        return not any(re.search(r"[A-Za-z]", item) for item in text)
