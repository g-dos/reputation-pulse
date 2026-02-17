from reputation_pulse.scoring import calculate_score


def test_calculate_score_uses_limits():
    data = {
        "followers": 2000,
        "stars": 1500,
        "recent_repos": [{}, {}, {}, {}],
    }
    score = calculate_score(data)
    assert score.normalized == 100.0


def test_calculate_score_handles_zero():
    score = calculate_score({"followers": 0, "stars": 0, "recent_repos": []})
    assert score.normalized == 0.0
