from pathlib import Path
from sigsurvey_rf.core import find_band, scan, parse_survey_csv
D = Path(__file__).parent.parent / "demos"
def test_band_lookup():
    b = find_band(2_412_000_000)
    assert b is not None and "ISM" in b["use"]
def test_gps_band():
    b = find_band(1_227_600_000)
    assert b is not None and "GPS" in b["use"]
def test_scan():
    r = scan(str(D))
    ids = {f.id for f in r.findings}
    # Should flag the 243MHz mil-UHF and the GPS L2 interference
    assert any(i.startswith("SR-FED") for i in ids)
    assert any(i.startswith("SR-GPS") for i in ids)
def test_parse():
    rows = parse_survey_csv(D / "survey.csv")
    assert len(rows) == 6
