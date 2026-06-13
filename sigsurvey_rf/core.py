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
# Source: FCC Online Table of Frequency Allocations (47 CFR §2.106)
BAND_PLAN = [
    # (low_hz, high_hz, primary_use, allocation, restrictions)
    (    9000,   148_500, "ELF/VLF nav",         "Federal",          "No general civilian transmit"),
    ( 148_500,   525_000, "AM broadcast adjacent","Mixed",            "Broadcast service rules"),
    ( 1_605_000, 1_705_000,"AM expanded",        "Broadcast",        ""),
    ( 27_000_000, 27_410_000,"CB radio",        "Personal",          "11m band: 4W AM / 12W SSB"),
    ( 88_000_000, 108_000_000,"FM broadcast",   "Broadcast",         ""),
    (108_000_000, 137_000_000,"Aeronautical",   "Federal",           "Air-to-ground; no civilian transmit"),
    (137_000_000, 138_000_000,"Space ops",      "Federal",           "Satellite downlink"),
    (148_000_000, 149_900_000,"Mobile sat (uplink)","Federal",       "Restricted; coordination required"),
    (162_400_000, 162_550_000,"NOAA wx radio",   "Federal",          "Broadcast only"),
    (225_000_000, 400_000_000,"Military UHF",    "Federal/DoD",      "Government use only"),
    (1_215_000_000, 1_300_000_000,"GPS L1/L2",  "Federal",            "Critical infra — no transmit"),
    (1_525_000_000, 1_559_000_000,"GPS L1",     "Federal",            "Critical infra — no transmit"),
    (2_320_000_000, 2_345_000_000,"Sirius/XM",  "Broadcast",          ""),
    (2_400_000_000, 2_500_000_000,"ISM (WiFi)",  "Unlicensed",        "Part 15"),
    (5_000_000_000, 5_250_000_000,"UNII-1",     "Unlicensed",         "Part 15, ≤200mW indoor"),
    (5_725_000_000, 5_875_000_000,"UNII-3",     "Unlicensed",         "Part 15, ≤4W EIRP"),
]

def find_band(freq_hz: int):
    for low, high, use, alloc, restr in BAND_PLAN:
        if low <= freq_hz < high: return {"low":low,"high":high,"use":use,"alloc":alloc,"restr":restr}
    return None

def parse_survey_csv(path: Path) -> list[dict]:
    """CSV columns: timestamp, freq_hz, power_dbm, bw_hz (any subset OK)."""
    rows = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                rows.append({
                    "freq_hz": int(float(r.get("freq_hz", 0))),
                    "power_dbm": float(r.get("power_dbm", -100)),
                    "bw_hz": int(float(r.get("bw_hz", 0))),
                    "ts": r.get("timestamp", ""),
                })
            except (ValueError, KeyError): continue
    return rows

def scan(target=".", **opts):
    r = ScanResult(tool_name="sigsurvey-rf", tool_version="0.1.0")
    p = Path(target)
    files = list(p.glob("*.csv")) if p.is_dir() else ([p] if p.suffix == ".csv" else [])
    r.items_scanned = len(files)
    for f in files:
        rows = parse_survey_csv(f)
        for i, row in enumerate(rows):
            band = find_band(row["freq_hz"])
            if not band:
                r.add(Finding(f"SR-UNK-{i:03d}", Severity.LOW,
                              f"{row['freq_hz']/1e6:.3f} MHz: outside known FCC band plan",
                              location=str(f),
                              remediation="Verify against your local NTIA allocation"))
                continue
            # Flag transmissions in federal/DoD/critical-infra bands with positive power
            if row["power_dbm"] > -90 and "Federal" in band["alloc"]:
                r.add(Finding(f"SR-FED-{i:03d}", Severity.HIGH,
                              f"Transmission in federal band: {row['freq_hz']/1e6:.3f} MHz ({band['use']})",
                              location=f"{f}:{i}",
                              description=f"Power {row['power_dbm']:.1f} dBm in {band['use']} band. {band['restr']}",
                              nist_800_53="SC-40", # wireless spec
                              remediation="If unintended emission, investigate source. If authorized, document NTIA coordination."))
            if "GPS" in band["use"] and row["power_dbm"] > -100:
                r.add(Finding(f"SR-GPS-{i:03d}", Severity.VERY_HIGH,
                              f"Possible GPS interference at {row['freq_hz']/1e6:.3f} MHz",
                              location=f"{f}:{i}",
                              remediation="Critical infrastructure band. Report to FCC ENF / Coast Guard NAVCEN."))
    r.finalize(); return r
