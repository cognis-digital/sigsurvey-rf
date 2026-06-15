"""sigsurvey-rf — RF spectrum survey + band-plan compliance.

Cognis additions only. Upstream (GNU Radio / GQRX) is GPL-3. Public band
plan data only (FCC Online Table of Frequency Allocations, NTIA "Red Book"
public version). Nothing classified, nothing ITAR.
"""
from __future__ import annotations

import csv
from pathlib import Path

from cognis_mil import ScanResult, Finding, Severity

# Public FCC/NTIA band plan (highly abridged, public-domain)
# Source: FCC Online Table of Frequency Allocations (47 CFR SS2.106)
BAND_PLAN = [
    # (low_hz, high_hz, primary_use, allocation, restrictions)
    (9000, 148_500, "ELF/VLF nav", "Federal", "No general civilian transmit"),
    (148_500, 525_000, "AM broadcast adjacent", "Mixed", "Broadcast service rules"),
    (1_605_000, 1_705_000, "AM expanded", "Broadcast", ""),
    (27_000_000, 27_410_000, "CB radio", "Personal", "11m band: 4W AM / 12W SSB"),
    (88_000_000, 108_000_000, "FM broadcast", "Broadcast", ""),
    (108_000_000, 137_000_000, "Aeronautical", "Federal", "Air-to-ground; no civilian transmit"),
    (137_000_000, 138_000_000, "Space ops", "Federal", "Satellite downlink"),
    (148_000_000, 149_900_000, "Mobile sat (uplink)", "Federal", "Restricted; coordination required"),
    (162_400_000, 162_550_000, "NOAA wx radio", "Federal", "Broadcast only"),
    (225_000_000, 400_000_000, "Military UHF", "Federal/DoD", "Government use only"),
    (1_215_000_000, 1_300_000_000, "GPS L1/L2", "Federal", "Critical infra - no transmit"),
    (1_525_000_000, 1_559_000_000, "GPS L1", "Federal", "Critical infra - no transmit"),
    (2_320_000_000, 2_345_000_000, "Sirius/XM", "Broadcast", ""),
    (2_400_000_000, 2_500_000_000, "ISM (WiFi)", "Unlicensed", "Part 15"),
    (5_000_000_000, 5_250_000_000, "UNII-1", "Unlicensed", "Part 15, <=200mW indoor"),
    (5_725_000_000, 5_875_000_000, "UNII-3", "Unlicensed", "Part 15, <=4W EIRP"),
]


def find_band(freq_hz):
    """Return the matching BAND_PLAN entry dict, or None.

    Accepts int or float; returns None for None, negative, or non-numeric input.
    """
    if freq_hz is None:
        return None
    try:
        freq_hz = int(freq_hz)
    except (TypeError, ValueError):
        return None
    if freq_hz < 0:
        return None
    for low, high, use, alloc, restr in BAND_PLAN:
        if low <= freq_hz < high:
            return {"low": low, "high": high, "use": use, "alloc": alloc, "restr": restr}
    return None


def parse_survey_csv(path):
    """Parse a survey CSV file.  Returns a (possibly empty) list of row dicts.

    CSV columns: timestamp, freq_hz, power_dbm, bw_hz (any subset OK).
    Raises FileNotFoundError if *path* does not exist.
    Raises OSError if the file cannot be read.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Survey file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Expected a file, got: {path}")

    rows = []
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                return rows  # empty file
            for r in reader:
                try:
                    freq_raw = r.get("freq_hz", "") or "0"
                    power_raw = r.get("power_dbm", "") or "-100"
                    bw_raw = r.get("bw_hz", "") or "0"
                    freq = int(float(freq_raw))
                    power = float(power_raw)
                    bw = int(float(bw_raw))
                    rows.append({
                        "freq_hz": freq,
                        "power_dbm": power,
                        "bw_hz": bw,
                        "ts": r.get("timestamp", ""),
                    })
                except (ValueError, KeyError):
                    continue  # skip malformed rows silently
    except OSError as exc:
        raise OSError(f"Cannot read survey file {path}: {exc}") from exc
    return rows


def scan(target=".", **opts):
    """Scan *target* (directory of CSVs or a single CSV file).

    On bad input a ScanResult with a diagnostic Finding is returned rather
    than raising, so the CLI always produces structured output.
    """
    r = ScanResult(tool_name="sigsurvey-rf", tool_version="0.1.0")
    p = Path(target)

    # --- path validation -------------------------------------------------
    if not p.exists():
        r.add(Finding(
            "SR-ERR-001", Severity.HIGH,
            f"Target path does not exist: {target}",
            remediation="Pass a valid directory or .csv file path.",
        ))
        r.finalize()
        return r

    if p.is_dir():
        files = list(p.glob("*.csv"))
    elif p.suffix.lower() == ".csv":
        files = [p]
    else:
        r.add(Finding(
            "SR-ERR-002", Severity.LOW,
            f"Target is not a .csv file or directory: {target}",
            remediation="Pass a CSV file or a directory containing CSV files.",
        ))
        r.finalize()
        return r

    r.items_scanned = len(files)

    if not files:
        # No CSVs found — valid but empty result; nothing to flag.
        r.finalize()
        return r

    for f in files:
        try:
            rows = parse_survey_csv(f)
        except (OSError, ValueError) as exc:
            r.add(Finding(
                "SR-ERR-003", Severity.MODERATE,
                f"Could not parse {f.name}: {exc}",
                location=str(f),
                remediation="Check the file is a readable UTF-8 CSV.",
            ))
            continue

        for i, row in enumerate(rows):
            freq = row["freq_hz"]
            power = row["power_dbm"]

            band = find_band(freq)
            if band is None:
                r.add(Finding(
                    f"SR-UNK-{i:03d}", Severity.LOW,
                    f"{freq / 1e6:.3f} MHz: outside known FCC band plan",
                    location=str(f),
                    remediation="Verify against your local NTIA allocation",
                ))
                continue

            # Flag transmissions in federal/DoD/critical-infra bands
            if power > -90 and "Federal" in band["alloc"]:
                r.add(Finding(
                    f"SR-FED-{i:03d}", Severity.HIGH,
                    f"Transmission in federal band: {freq / 1e6:.3f} MHz ({band['use']})",
                    location=f"{f}:{i}",
                    description=(
                        f"Power {power:.1f} dBm in {band['use']} band. {band['restr']}"
                    ),
                    nist_800_53="SC-40",
                    remediation=(
                        "If unintended emission, investigate source. "
                        "If authorized, document NTIA coordination."
                    ),
                ))

            if "GPS" in band["use"] and power > -100:
                r.add(Finding(
                    f"SR-GPS-{i:03d}", Severity.VERY_HIGH,
                    f"Possible GPS interference at {freq / 1e6:.3f} MHz",
                    location=f"{f}:{i}",
                    remediation=(
                        "Critical infrastructure band. "
                        "Report to FCC ENF / Coast Guard NAVCEN."
                    ),
                ))

    r.finalize()
    return r
