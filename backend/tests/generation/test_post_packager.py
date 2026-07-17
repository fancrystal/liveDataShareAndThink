import json

import httpx

from app.generation.post_packager import DeepSeekPostPackager


def test_post_packager_requires_chinese_only_output() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"title": "北京火锅探店", "caption": "探店内容", "tags": ["北京火锅"], "pages": [{"heading": f"第{number}页", "body": "中文内容"} for number in range(1, 6)]}, ensure_ascii=False)}}]})

    result = DeepSeekPostPackager("key", "model", client=httpx.Client(transport=httpx.MockTransport(handler))).create("北京火锅", "探店", [])

    assert result["title"] == "北京火锅探店"
    assert "中文" in captured["messages"][0]["content"]
    assert "英文" in captured["messages"][0]["content"]


def test_post_packager_retries_once_after_an_invalid_model_structure() -> None:
    responses = [
        {"choices": [{"message": {"content": json.dumps({"title": "第一次", "caption": "内容", "tags": [], "pages": []}, ensure_ascii=False)}}]},
        {"choices": [{"message": {"content": json.dumps({"title": "第二次", "caption": "内容", "tags": [], "pages": [{"heading": f"第{number}页", "body": "中文内容"} for number in range(1, 6)]}, ensure_ascii=False)}}]},
    ]

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=responses.pop(0))

    result = DeepSeekPostPackager("key", "model", client=httpx.Client(transport=httpx.MockTransport(handler))).create("北京火锅", "探店", [])

    assert result["title"] == "第二次"
    assert responses == []


def test_post_packager_retries_when_model_mixes_english_into_content() -> None:
    responses = [
        {"choices": [{"message": {"content": json.dumps({"title": "北京火锅top3", "caption": "内容", "tags": [], "pages": [{"heading": f"第{number}页", "body": "中文内容"} for number in range(1, 6)]}, ensure_ascii=False)}}]},
        {"choices": [{"message": {"content": json.dumps({"title": "北京火锅推荐", "caption": "内容", "tags": [], "pages": [{"heading": f"第{number}页", "body": "中文内容"} for number in range(1, 6)]}, ensure_ascii=False)}}]},
    ]

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=responses.pop(0))

    result = DeepSeekPostPackager("key", "model", client=httpx.Client(transport=httpx.MockTransport(handler))).create("北京火锅", "探店", [])

    assert result["title"] == "北京火锅推荐"
