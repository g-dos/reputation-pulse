from __future__ import annotations

from dataclasses import dataclass

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.scan_service import ScanService
from reputation_pulse.storage import ScanStore


@dataclass(frozen=True)
class RuntimeContainer:
    analyzer: ReputationAnalyzer
    store: ScanStore
    scan_service: ScanService


def build_runtime() -> RuntimeContainer:
    analyzer = ReputationAnalyzer()
    store = ScanStore()
    scan_service = ScanService(analyzer=analyzer, store=store)
    return RuntimeContainer(analyzer=analyzer, store=store, scan_service=scan_service)
