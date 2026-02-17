from reputation_pulse.html_report import render_html_report


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
