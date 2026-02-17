from __future__ import annotations

from typing import Any

from reputation_pulse.collectors.github import GitHubCollector
from reputation_pulse.reports import build_summary
from reputation_pulse.scoring import calculate_score


class ReputationAnalyzer:
    def __init__(self, github_collector: GitHubCollector | None = None) -> None:
        self.github_collector = github_collector or GitHubCollector()

    async def run(self, handle: str) -> dict[str, Any]:
        github_data = await self.github_collector.collect(handle)
        score = calculate_score(github_data)
        summary = build_summary(github_data, score)
        return {
            "handle": handle,
            "github": github_data,
            "score": score.to_dict(),
            "summary": summary,
        }
