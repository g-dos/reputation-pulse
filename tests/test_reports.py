from reputation_pulse.reports import build_summary
from reputation_pulse.scoring import ReputationScore


def test_build_summary_with_low_score():
    github_data = {"followers": 10, "stars": 5, "public_repos": 1, "recent_repos": []}
    score = ReputationScore(followers=10, stars=5, recent_repos=0, normalized=10.5)
    summary = build_summary(github_data, score)

    assert summary["rating"] == "Needs Attention"
    assert summary["recommendations"]


def test_build_summary_rating_thresholds():
    github_data = {
        "followers": 1000,
        "stars": 2000,
        "public_repos": 5,
        "recent_repos": [{"name": "foo"}],
    }
    score = ReputationScore(followers=1000, stars=2000, recent_repos=1, normalized=95.0)
    summary = build_summary(github_data, score)

    assert summary["rating"] == "Strong"


def test_build_summary_adds_web_recommendation():
    github_data = {
        "followers": 100,
        "stars": 200,
        "public_repos": 5,
        "recent_repos": [{"name": "foo"}],
    }
    score = ReputationScore(followers=100, stars=200, recent_repos=1, normalized=50.0)
    summary = build_summary(
        github_data,
        score,
        web_data={"blog_url": "https://example.com", "recent_entries_30d": 0},
    )
    assert any("blog" in item.lower() for item in summary["recommendations"])
