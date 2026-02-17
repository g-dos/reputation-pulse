from __future__ import annotations

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.storage import ScanStore
from reputation_pulse.trends import build_trend


class ScanService:
    def __init__(
        self,
        analyzer: ReputationAnalyzer | None = None,
        store: ScanStore | None = None,
    ) -> None:
        self.analyzer = analyzer or ReputationAnalyzer()
        self.store = store or ScanStore()

    async def run_and_store(self, handle: str) -> dict[str, object]:
        result = await self.analyzer.run(handle)
        previous = self.store.latest_scan_for_handle(str(result["handle"]))
        previous_score = None if previous is None else float(previous["normalized_score"])
        result["trend"] = build_trend(float(result["score"]["normalized"]), previous_score)
        self.store.save_scan(result)
        return result
