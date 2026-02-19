from __future__ import annotations


def sparkline_svg(points: list[float]) -> str:
    if not points:
        return "<p>No history yet.</p>"
    if len(points) == 1:
        return "<p>Not enough history points for trend chart.</p>"

    width = 560
    height = 120
    padding = 12
    min_value = min(points)
    max_value = max(points)
    value_range = max(max_value - min_value, 1.0)
    step = (width - (padding * 2)) / (len(points) - 1)

    svg_points: list[str] = []
    for idx, value in enumerate(points):
        x = padding + (idx * step)
        normalized = (value - min_value) / value_range
        y = (height - padding) - (normalized * (height - (padding * 2)))
        svg_points.append(f"{x:.2f},{y:.2f}")

    polyline = " ".join(svg_points)
    min_text = (
        f'<text x="{padding}" y="{height - 2}" fill="#6b7280" '
        f'font-size="10">{min_value:.1f}</text>'
    )
    max_x = width - padding - 28
    max_text = (
        f'<text x="{max_x}" y="{height - 2}" fill="#6b7280" '
        f'font-size="10">{max_value:.1f}</text>'
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
        'role="img" aria-label="Score history chart">'
        f'<polyline fill="none" stroke="#2563eb" stroke-width="3" points="{polyline}" />'
        f"{min_text}"
        f"{max_text}"
        "</svg>"
    )
