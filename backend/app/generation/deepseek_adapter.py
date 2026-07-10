import json
from typing import Any

import httpx

from app.generation.ports import GeneratedContent, GenerationBrief


class DeepSeekGenerationError(RuntimeError):
    pass


class DeepSeekGenerator:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.deepseek.com",
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)

    @property
    def name(self) -> str:
        return f"deepseek:{self.model}"

    def generate(self, brief: GenerationBrief) -> list[GeneratedContent]:
        payload = {
            "model": self.model,
            "temperature": 0.8,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是小红书内容策略师。只能返回一个 JSON 对象，不要 Markdown。"
                        "对象必须包含 variants 数组，数组恰好三项，variant 分别为 practical、story、contrarian。"
                        "每项必须包含 title、body、tags、cover_text。标题不超过20个汉字，"
                        "必须原创，不得逐句复述参考样本。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "topic": brief.topic,
                            "audience": brief.audience,
                            "goal": brief.goal,
                            "angle": brief.angle,
                            "brand_tone": brief.brand_tone,
                            "forbidden_terms": brief.forbidden_terms,
                            "evidence": brief.evidence_summaries,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise DeepSeekGenerationError("DeepSeek generation request failed") from error
        return self._parse_variants(parsed)

    @staticmethod
    def _parse_variants(payload: dict[str, Any]) -> list[GeneratedContent]:
        variants = payload.get("variants")
        if not isinstance(variants, list) or len(variants) != 3:
            raise DeepSeekGenerationError("DeepSeek did not return exactly three variants")
        result: list[GeneratedContent] = []
        expected = {"practical", "story", "contrarian"}
        for item in variants:
            if not isinstance(item, dict) or not expected.issuperset({item.get("variant")}):
                raise DeepSeekGenerationError("DeepSeek returned an invalid variant")
            tags = item.get("tags")
            if not all(isinstance(value, str) for value in tags or []):
                raise DeepSeekGenerationError("DeepSeek returned invalid tags")
            result.append(
                GeneratedContent(
                    variant=item["variant"],
                    title=str(item.get("title", "")),
                    body=str(item.get("body", "")),
                    tags=tuple(tags),
                    cover_text=str(item.get("cover_text", "")),
                )
            )
        if {item.variant for item in result} != expected:
            raise DeepSeekGenerationError("DeepSeek variants must be unique")
        return result
