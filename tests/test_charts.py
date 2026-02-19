from reputation_pulse.charts import sparkline_svg


def test_sparkline_svg_empty():
    assert "No history yet" in sparkline_svg([])


def test_sparkline_svg_single_point():
    assert "Not enough history points" in sparkline_svg([10.0])


def test_sparkline_svg_multi_point():
    svg = sparkline_svg([10.0, 20.0, 15.0])
    assert "<svg" in svg
    assert "polyline" in svg
