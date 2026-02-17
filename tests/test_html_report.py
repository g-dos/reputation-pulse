from reputation_pulse.html_report import default_report_path, render_html_report


def test_render_html_report_contains_key_fields():
    result = {
        "handle": "g-dos",
        "github": {"followers": 10, "stars": 5},
        "score": {"normalized": 32.5},
        "summary": {"rating": "Needs Attention", "recommendations": ["Ship more commits"]},
        "trend": {"direction": "up", "delta": 2.0},
    }
    html = render_html_report(result)
    assert "Reputation Pulse Report: g-dos" in html
    assert "Needs Attention" in html
    assert "Ship more commits" in html


def test_render_html_report_escapes_user_content():
    result = {
        "handle": "<script>alert(1)</script>",
        "github": {"followers": 1, "stars": 1},
        "score": {"normalized": 10.0},
        "summary": {"rating": "ok", "recommendations": ["<img src=x onerror=alert(1)>"]},
        "trend": {"direction": "up", "delta": 1.0},
    }
    html = render_html_report(result)
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html


def test_default_report_path_format():
    path = default_report_path("g-dos")
    assert path.startswith("reports/g-dos-")
    assert path.endswith(".html")


def test_render_html_report_with_series_has_svg():
    result = {
        "handle": "g-dos",
        "github": {"followers": 10, "stars": 5},
        "score": {"normalized": 32.5},
        "summary": {"rating": "Needs Attention", "recommendations": []},
        "trend": {"direction": "up", "delta": 2.0},
    }
    series = [{"normalized_score": 10.0}, {"normalized_score": 15.0}, {"normalized_score": 32.5}]
    html = render_html_report(result, score_series=series)
    assert "<svg" in html
    assert "Score History" in html
