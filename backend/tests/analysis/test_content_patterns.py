from app.analysis.patterns import ContentSample, derive_content_attraction_patterns


def test_content_patterns_return_traceable_hook_format_and_angles() -> None:
    result = derive_content_attraction_patterns(
        [
            ContentSample("note-1", "敏感肌先做减法", "先停用刺激产品，再保留基础保湿。", "image"),
            ContentSample("note-2", "泛红时别急着修护", "两个步骤检查刺激来源。", "video"),
            ContentSample("note-3", "为什么越护肤越红？", "记录产品和反应，减少试错。", "image"),
        ]
    )

    assert result.hook_patterns["directive"] == 2
    assert result.hook_patterns["question"] == 1
    assert result.format_counts == {"image": 2, "video": 1}
    assert len(result.reusable_angles) == 3
    assert result.note_ids == ("note-1", "note-2", "note-3")
