from reputation_pulse.reports import build_summary
from reputation_pulse.scoring import ReputationScore


def test_build_summary_with_low_score():
    github_data = {"followers": 10, "stars": 5, "public_repos": 1, "recent_repos": []}
    score = ReputationScore(followers=10, stars=5, recent_repos=0, normalized=10.5)
    summary = build_summary(github_data, score)

    assert summary["rating"] == "Needs Attention"
    assert summary["recommendations"]


def test_build_summary_rating_thresholds():
    github_data = {"followers": 1000, "stars": 2000, "public_repos": 5, "recent_repos": [{"name": "foo"}]}
    score = ReputationScore(followers=1000, stars=2000, recent_repos=1, normalized=95.0)
    summary = build_summary(github_data, score)

    assert summary["rating"] == "Strong"
