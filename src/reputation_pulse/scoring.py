from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReputationScore:
    followers: int
    stars: int
    recent_repos: int
    normalized: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def calculate_score(github_data: dict[str, int | list[dict[str, int]]]) -> ReputationScore:
    followers = github_data.get("followers", 0)
    stars = github_data.get("stars", 0)
    recent_repos = len(github_data.get("recent_repos", []))

    followers_score = min(followers, 500) / 500 * 30
    stars_score = min(stars, 1000) / 1000 * 40
    recent_score = min(recent_repos, 3) / 3 * 30

    normalized = round(followers_score + stars_score + recent_score, 2)

    return ReputationScore(
        followers=followers,
        stars=stars,
        recent_repos=recent_repos,
        normalized=normalized,
    )
