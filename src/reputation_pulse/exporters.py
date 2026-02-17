from __future__ import annotations

import csv
import io
import json
from pathlib import Path


def insights_to_json(insight: dict[str, object]) -> str:
    return json.dumps(insight, indent=2)


def insights_to_csv(insight: dict[str, object]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["field", "value"])
    for key, value in insight.items():
        writer.writerow([key, value])
    return buffer.getvalue()


def write_export(content: str, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)
