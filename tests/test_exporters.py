from reputation_pulse.exporters import insights_to_csv, insights_to_json


def test_insights_to_json():
    payload = insights_to_json({"handle": "g-dos", "scans_count": 2})
    assert '"handle": "g-dos"' in payload


def test_insights_to_csv():
    payload = insights_to_csv({"handle": "g-dos", "scans_count": 2})
    assert "field,value" in payload
    assert "handle,g-dos" in payload
