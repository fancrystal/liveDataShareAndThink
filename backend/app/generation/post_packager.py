import json
import re
from typing import Any

import httpx


class DeepSeekPostPackager:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.deepseek.com", client: httpx.Client | None = None) -> None:
        self.api_key, self.model, self.base_url = api_key, model, base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    def create(self, topic: str, angle: str, evidence: list[str]) -> dict[str, Any]:
        request = {"topic": topic, "angle": angle, "evidence": evidence, "required_json": ["title", "caption", "tags", "pages"]}
        messages = [
            {
                "role": "system",
                "content": "只返回 JSON。请依据提供的公开素材，创作原创小红书图文。标题、正文、标签、每页标题和每页文案必须全部使用简体中文，不得使用英文或英文缩写。pages 必须恰好有 5 项，每项均含 heading 和 body。不得编造未提供的事实或医疗效果。",
            },
            {"role": "user", "content": json.dumps(request, ensure_ascii=False)},
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
                result = json.loads(response.json()["choices"][0]["message"]["content"])
                if self._is_valid(result):
                    return result
                last_error = RuntimeError("DeepSeek post package response is invalid")
            except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
                last_error = error

            if attempt == 0:
                messages.append({"role": "user", "content": "上一次结果不可用。请严格按要求重新输出完整的 5 页中文 JSON，不要附加解释。"})

        raise RuntimeError("DeepSeek post package request failed") from last_error

    @staticmethod
    def _is_valid(result: Any) -> bool:
        is_structurally_valid = (
            isinstance(result, dict)
            and isinstance(result.get("title"), str)
            and isinstance(result.get("caption"), str)
            and isinstance(result.get("tags"), list)
            and all(isinstance(tag, str) for tag in result["tags"])
            and isinstance(result.get("pages"), list)
            and len(result["pages"]) == 5
            and all(isinstance(page, dict) and isinstance(page.get("heading"), str) and isinstance(page.get("body"), str) for page in result["pages"])
        )
        if not is_structurally_valid:
            return False

        text = [result["title"], result["caption"], *result["tags"]]
        text.extend(part for page in result["pages"] for part in (page["heading"], page["body"]))
        return not any(re.search(r"[A-Za-z]", item) for item in text)
