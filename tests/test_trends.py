from reputation_pulse.trends import build_trend


def test_build_trend_new():
    trend = build_trend(50.0, None)
    assert trend["direction"] == "new"
    assert trend["delta"] == 0.0


def test_build_trend_up():
    trend = build_trend(70.0, 60.0)
    assert trend["direction"] == "up"
    assert trend["delta"] == 10.0


def test_build_trend_down():
    trend = build_trend(30.0, 50.0)
    assert trend["direction"] == "down"
    assert trend["delta"] == -20.0
