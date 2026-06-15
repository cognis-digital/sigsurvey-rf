"""Tests for hardened error-handling and edge-case paths in sigsurvey-rf."""
from __future__ import annotations

from pathlib import Path

import pytest

from sigsurvey_rf.core import find_band, parse_survey_csv, scan

DEMOS = Path(__file__).parent.parent / "demos"


# ---------------------------------------------------------------------------
# find_band edge cases
# ---------------------------------------------------------------------------

def test_find_band_none_input():
    """None frequency must return None without raising."""
    assert find_band(None) is None


def test_find_band_negative_freq():
    """Negative frequency is physically meaningless; must return None."""
    assert find_band(-1_000_000) is None


def test_find_band_non_numeric_string():
    """A non-numeric string must return None, not raise."""
    assert find_band("not-a-number") is None  # type: ignore[arg-type]


def test_find_band_float_input():
    """Float frequency should be accepted (coerced to int)."""
    result = find_band(2_412_000_000.0)
    assert result is not None and "ISM" in result["use"]


def test_find_band_zero():
    """Zero is below all bands and should return None."""
    assert find_band(0) is None


# ---------------------------------------------------------------------------
# parse_survey_csv error paths
# ---------------------------------------------------------------------------

def test_parse_missing_file(tmp_path: Path):
    """Missing file must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_survey_csv(tmp_path / "does_not_exist.csv")


def test_parse_empty_csv(tmp_path: Path):
    """Completely empty CSV file should return an empty list, not raise."""
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    rows = parse_survey_csv(empty)
    assert rows == []


def test_parse_header_only_csv(tmp_path: Path):
    """CSV with only a header row should return empty list."""
    f = tmp_path / "header_only.csv"
    f.write_text("timestamp,freq_hz,power_dbm,bw_hz\n", encoding="utf-8")
    rows = parse_survey_csv(f)
    assert rows == []


def test_parse_malformed_rows_skipped(tmp_path: Path):
    """Rows with non-numeric freq_hz should be silently skipped; valid rows kept."""
    f = tmp_path / "mixed.csv"
    f.write_text(
        "timestamp,freq_hz,power_dbm,bw_hz\n"
        "2026-01-01,2412000000,-50,20000000\n"
        "2026-01-01,GARBAGE,-50,20000000\n"
        "2026-01-01,5180000000,-65,80000000\n",
        encoding="utf-8",
    )
    rows = parse_survey_csv(f)
    assert len(rows) == 2
    assert rows[0]["freq_hz"] == 2_412_000_000
    assert rows[1]["freq_hz"] == 5_180_000_000


def test_parse_missing_optional_columns(tmp_path: Path):
    """CSV with only freq_hz column should not raise; defaults apply."""
    f = tmp_path / "minimal.csv"
    f.write_text("freq_hz\n2412000000\n", encoding="utf-8")
    rows = parse_survey_csv(f)
    assert len(rows) == 1
    assert rows[0]["power_dbm"] == -100.0
    assert rows[0]["bw_hz"] == 0


# ---------------------------------------------------------------------------
# scan() error / edge-case paths
# ---------------------------------------------------------------------------

def test_scan_nonexistent_target():
    """scan() on a missing path should return a result with SR-ERR-001, not raise."""
    result = scan("/this/path/absolutely/does/not/exist")
    ids = {f.id for f in result.findings}
    assert "SR-ERR-001" in ids


def test_scan_non_csv_file(tmp_path: Path):
    """scan() on a non-.csv file should return SR-ERR-002 finding."""
    txt = tmp_path / "data.txt"
    txt.write_text("hello\n")
    result = scan(str(txt))
    ids = {f.id for f in result.findings}
    assert "SR-ERR-002" in ids


def test_scan_empty_directory(tmp_path: Path):
    """scan() on a directory with no CSV files should return a clean result."""
    result = scan(str(tmp_path))
    assert result.items_scanned == 0
    assert result.total_findings() == 0


def test_scan_unreadable_csv_produces_error_finding(tmp_path: Path):
    """scan() on a directory with an unreadable CSV produces an SR-ERR-003 finding."""
    bad_csv = tmp_path / "unreadable.csv"
    bad_csv.write_text("timestamp,freq_hz,power_dbm,bw_hz\n")
    # Make it a directory to trigger ValueError (is not a file)
    bad_csv.unlink()
    bad_csv.mkdir()
    result = scan(str(tmp_path))
    ids = {f.id for f in result.findings}
    assert "SR-ERR-003" in ids


def test_scan_single_csv_file(tmp_path: Path):
    """scan() should accept a direct path to a single .csv file."""
    csv_file = tmp_path / "single.csv"
    csv_file.write_text(
        "timestamp,freq_hz,power_dbm,bw_hz\n"
        "2026-01-01,2412000000,-50,20000000\n",
        encoding="utf-8",
    )
    result = scan(str(csv_file))
    assert result.items_scanned == 1


def test_scan_result_is_always_finalized():
    """finalize() should always be called; composite_score should be a float."""
    result = scan("/nonexistent/path")
    assert isinstance(result.composite_score, float)
