from __future__ import annotations


def build_trend(current_score: float, previous_score: float | None) -> dict[str, object]:
    if previous_score is None:
        return {"direction": "new", "delta": 0.0, "previous_score": None}

    delta = round(current_score - previous_score, 2)
    if delta > 0:
        direction = "up"
    elif delta < 0:
        direction = "down"
    else:
        direction = "stable"

    return {"direction": direction, "delta": delta, "previous_score": previous_score}
