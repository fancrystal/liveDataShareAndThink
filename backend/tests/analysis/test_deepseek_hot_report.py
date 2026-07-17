import json

import httpx


def test_deepseek_hot_report_returns_reasons_and_replication_checklist() -> None:
    from app.analysis.deepseek_reporter import DeepSeekHotReporter

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
            "today_summary": "产后修复话题以低门槛动作受关注",
            "hot_reasons": ["明确人群", "可执行步骤"],
            "replication_checklist": ["先写痛点", "给出动作"],
            "disclosure": "发布时间未公开"
        })}}]})

    reporter = DeepSeekHotReporter("key", "model", client=httpx.Client(transport=httpx.MockTransport(handler)))
    report = reporter.analyze("普拉提产后修复", [{"title": "产后修复先做什么", "likes": 1200}])

    assert report["hot_reasons"] == ["明确人群", "可执行步骤"]
    assert report["disclosure"] == "发布时间未公开"
