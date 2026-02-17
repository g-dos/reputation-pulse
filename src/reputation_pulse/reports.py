from __future__ import annotations

from reputation_pulse.scoring import ReputationScore


def _rating_label(normalized: float) -> str:
    if normalized >= 70:
        return "Strong"
    if normalized >= 40:
        return "Stable"
    return "Needs Attention"


def build_summary(
    github_data: dict[str, object],
    score: ReputationScore,
    web_data: dict[str, object] | None = None,
) -> dict[str, object]:
    recommendations: list[str] = []

    if github_data.get("public_repos", 0) < 3:
        recommendations.append("Publish at least 2-3 public projects to show momentum.")

    if github_data.get("followers", 0) < 50:
        recommendations.append("Engage with communities (issues/comments) to grow followers.")

    if not github_data.get("recent_repos"):
        recommendations.append("Push a recent change to demonstrate active work.")

    if score.stars < 100:
        recommendations.append("Aim for a few high-quality repos to attract more stars.")

    if web_data and web_data.get("blog_url"):
        if int(web_data.get("recent_entries_30d", 0)) == 0:
            recommendations.append(
                "Publish a technical update on your blog or RSS to keep visibility active."
            )

    return {
        "rating": _rating_label(score.normalized),
        "normalized": score.normalized,
        "recommendations": recommendations,
    }
