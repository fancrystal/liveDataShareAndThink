from app.analysis.scoring import MetricInput, score_note


def test_small_author_outperformance_is_visible() -> None:
    score = score_note(
        MetricInput(
            likes=860,
            favorites=620,
            comments=143,
            shares=31,
            followers=1200,
            age_hours=24,
        ),
        cohort_median_engagement=600,
        cohort_size=3,
    )

    assert 0 <= score.total <= 100
    assert score.author_efficiency is not None
    assert score.author_efficiency > 80
    assert score.confidence == "high"
    assert score.explanation["followers"] == 1200


def test_missing_followers_reduce_confidence_without_becoming_zero() -> None:
    score = score_note(
        MetricInput(
            likes=50,
            favorites=20,
            comments=5,
            shares=None,
            followers=None,
            age_hours=12,
        ),
        cohort_median_engagement=80,
        cohort_size=3,
    )

    assert score.author_efficiency is None
    assert score.confidence == "medium"
    assert score.total > 0

