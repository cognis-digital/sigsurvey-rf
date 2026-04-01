# sigsurvey-rf — RF spectrum survey w/ FCC/NTIA compliance

[![CI](https://github.com/cognis-digital/sigsurvey-rf/workflows/CI/badge.svg)](https://github.com/cognis-digital/sigsurvey-rf/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Audit RF spectrum captures against the PUBLIC FCC band plan. Flag federal/DoD/GPS-band transmissions.

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

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).
