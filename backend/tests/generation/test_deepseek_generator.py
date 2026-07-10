import json

import httpx

from app.generation.deepseek_adapter import DeepSeekGenerator
from app.generation.ports import GenerationBrief


def test_deepseek_generator_sends_openai_compatible_request_and_parses_three_variants() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [{
                    "message": {
                        "content": """{
                          \"variants\": [
                            {\"variant\": \"practical\", \"title\": \"先做减法\", \"body\": \"正文一\", \"tags\": [\"敏感肌\"], \"cover_text\": \"减法\"},
                            {\"variant\": \"story\", \"title\": \"我的泛红记录\", \"body\": \"正文二\", \"tags\": [\"护肤\"], \"cover_text\": \"记录\"},
                            {\"variant\": \"contrarian\", \"title\": \"别急着修护\", \"body\": \"正文三\", \"tags\": [\"避坑\"], \"cover_text\": \"先停\"}
                          ]
                        }"""
                    }
                }]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    generator = DeepSeekGenerator(
        api_key="test-key",
        model="deepseek-v4-flash",
        client=client,
    )
    result = generator.generate(
        GenerationBrief(
            topic="敏感肌直播前先做减法",
            audience="敏感肌用户",
            goal="live_preview",
            angle="两步自查",
            brand_tone="专业、克制",
            forbidden_terms=(),
            evidence_summaries=("收藏和评论表现突出",),
        )
    )

    assert len(result) == 3
    assert result[0].variant == "practical"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "deepseek-v4-flash"
    assert captured["payload"]["messages"][1]["role"] == "user"
