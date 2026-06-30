# sigsurvey-rf — RF spectrum survey w/ FCC/NTIA compliance

[![CI](https://github.com/cognis-digital/sigsurvey-rf/workflows/CI/badge.svg)](https://github.com/cognis-digital/sigsurvey-rf/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Audit RF spectrum captures against the PUBLIC FCC band plan. Flag federal/DoD/GPS-band transmissions.


<!-- cognis:example:start -->
## 🔎 Example output

Real, reproducible output from the tool — runs offline:

```console
$ sigsurvey-rf-emit --version
sigsurvey-rf 0.1.0
```

```console
$ sigsurvey-rf-emit --help
usage: sigsurvey-rf [-h] [--format {console,json,markdown,sarif,oscal}]
                    [--out OUT] [--fail-on {very_high,high,moderate,low,none}]
                    [--classification CLASSIFICATION] [-v]
                    [target]

sigsurvey-rf — Cognis Digital · Military/IC ecosystem

positional arguments:
  target                Path/target

options:
  -h, --help            show this help message and exit
  --format {console,json,markdown,sarif,oscal}
  --out OUT             Write output to file
  --fail-on {very_high,high,moderate,low,none}
  --classification CLASSIFICATION
                        Operator-supplied banner. PLACEHOLDER. Tool does not
                        interpret.
  -v, --version         show program's version number and exit
```

> Blocks above are real `sigsurvey-rf` output — reproduce them from a clone.

**Sample result format** _(illustrative values — run on your own data for real findings):_

```
{
"incident_id": "1234567890",
"reporter": "John Doe",
"report_time": "2023-02-15T14:30:00Z",
"findings": [
  {
    "id": "1",
    "title": "Suspicious Network Traffic",
    "description": "Unusual network traffic detected from IP address 192.0.2.1",
    "confidence": 70,
    "severity": "medium"
  },
  {
    "id": "2",
    "title": "Malware Detection",
    "description": "Malware detected on system with ID 'abc123'",
    "confidence": 90,
    "severity": "high"
  }
]
}
```

<!-- cognis:example:end -->

## Usage — step by step

`sigsurvey-rf` uses the shared `cognis_mil` CLI: a positional target plus
standard output/scoring flags.

1. **Install** (editable from a clone, or from the wheel):
   ```bash
   pip install -e .
   # provides the `sigsurvey-rf` console script
   ```
2. **Run the primary scan** against a path or target (defaults to `.`):
   ```bash
   sigsurvey-rf .
   ```
3. **Emit machine-readable output** — `console|json|markdown|sarif|oscal`:
   ```bash
   sigsurvey-rf ./target --format json --out sigsurvey-report.json
   ```
4. **Read / use the output.** The JSON report holds the findings and a
   severity-weighted `composite_score`; `sarif` integrates with code-scanning
   and `oscal` emits an OSCAL skeleton. Stamp an operator banner with
   `--classification` (placeholder only — not interpreted by the tool):
   ```bash
   sigsurvey-rf ./target --classification "UNCLASSIFIED//FOR PUBLIC RELEASE" --format markdown
   ```
5. **Gate CI on severity** with `--fail-on` (`very_high|high|moderate|low|none`);
   the exit code is non-zero when a finding at/above the threshold is present:
   ```bash
   sigsurvey-rf ./target --format sarif --out sigsurvey.sarif --fail-on high
   ```

## Upstream

Forks / wraps **https://github.com/gnuradio/gnuradio**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- Band-plan validator using FCC §2.106 public data
- GPS L1/L2 interference detector (critical infra)
- Federal/DoD-band transmission flagger
- CSV ingest from any SDR survey tool

## Install

```bash
# Shared library (only once for the whole ecosystem):
pip install -e ../../shared

# This tool:
pip install -e .
```

## Demo

```bash
sigsurvey-rf demos/survey.csv
```

Outputs are available in five formats — all respect an operator-supplied
classification banner (passed via `--classification`):

```bash
sigsurvey-rf <target> --format=console     # default
sigsurvey-rf <target> --format=json
sigsurvey-rf <target> --format=sarif       # for code-scanning pipelines
sigsurvey-rf <target> --format=markdown    # for PRs / briefings
sigsurvey-rf <target> --format=oscal       # OSCAL Assessment Results skeleton
```

## Classification banner

All output is wrapped with an operator-supplied classification banner.
**Default**: `UNCLASSIFIED//FOR PUBLIC RELEASE`.

> ⚠️ This tool **does not** generate or validate the *content* of higher
> classifications. Operators on cleared systems supply real markings at runtime.
> See [`../shared/cognis_mil/classmark.py`](../../shared/cognis_mil/classmark.py).

## Compliance crosswalks (built in)

Every finding can carry references to:
- **NIST 800-53 Rev 5** controls (e.g. `AC-2(1)`)
- **DISA STIG** rule IDs (e.g. `V-242414`)
- **MITRE ATT&CK** technique IDs (e.g. `T1078`)
- **CCI** (Control Correlation Identifier)

These are emitted in JSON, SARIF, and the OSCAL skeleton.

## CI / RMF integration

```yaml
- name: sigsurvey-rf scan
  run: |
    pip install cognis-sigsurvey-rf
    sigsurvey-rf . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/COCL (Cognis Open Collaboration License)/GPL-3 (per upstream). Cognis additions are
COCL (Cognis Open Collaboration License) unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

## Interoperability

`sigsurvey-rf` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## Integrations

Forward `sigsurvey-rf`'s findings to STIX/MISP/Sigma/Splunk/Elastic/Slack/webhooks via
[`cognis-connect`](https://github.com/cognis-digital/cognis-connect). See **[INTEGRATIONS.md](INTEGRATIONS.md)**.
