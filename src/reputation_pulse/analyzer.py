from __future__ import annotations

from typing import Any

from reputation_pulse.collectors.github import GitHubCollector
from reputation_pulse.errors import InvalidHandleError
from reputation_pulse.reports import build_summary
from reputation_pulse.scoring import calculate_score


class ReputationAnalyzer:
    def __init__(self, github_collector: GitHubCollector | None = None) -> None:
        self.github_collector = github_collector or GitHubCollector()

    async def run(self, handle: str) -> dict[str, Any]:
        normalized_handle = handle.strip().lstrip("@")
        if not normalized_handle:
            raise InvalidHandleError("Handle cannot be empty")

        github_data = await self.github_collector.collect(normalized_handle)
        score = calculate_score(github_data)
        summary = build_summary(github_data, score)
        return {
            "handle": normalized_handle,
            "github": github_data,
            "score": score.to_dict(),
            "summary": summary,
        }
