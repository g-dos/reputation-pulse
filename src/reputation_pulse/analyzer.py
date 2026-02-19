from __future__ import annotations

from typing import Any

from reputation_pulse.collectors.github import GitHubCollector
from reputation_pulse.collectors.rss import RssCollector
from reputation_pulse.handles import normalize_handle
from reputation_pulse.reports import build_summary
from reputation_pulse.scoring import calculate_score


class ReputationAnalyzer:
    def __init__(
        self,
        github_collector: GitHubCollector | None = None,
        rss_collector: RssCollector | None = None,
    ) -> None:
        self.github_collector = github_collector or GitHubCollector()
        self.rss_collector = rss_collector or RssCollector()

    async def run(self, handle: str) -> dict[str, Any]:
        normalized_handle = normalize_handle(handle)
        github_data = await self.github_collector.collect(normalized_handle)
        web_data = await self.rss_collector.collect(str(github_data.get("blog_url", "")))
        score = calculate_score(github_data)
        summary = build_summary(github_data, score, web_data=web_data)
        return {
            "handle": normalized_handle,
            "github": github_data,
            "web": web_data,
            "score": score.to_dict(),
            "summary": summary,
        }
