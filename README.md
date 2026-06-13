# sigsurvey-rf — RF spectrum survey w/ FCC/NTIA compliance

[![CI](https://github.com/cognis-digital/sigsurvey-rf/workflows/CI/badge.svg)](https://github.com/cognis-digital/sigsurvey-rf/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Audit RF spectrum captures against the PUBLIC FCC band plan. Flag federal/DoD/GPS-band transmissions.

<!-- cognis:layman:start -->
## What is this?

sigsurvey-rf reads radio frequency (RF) measurement files from software-defined radio (SDR) tools and checks each detected signal against the public FCC and NTIA frequency band plan. It highlights signals that appear in restricted government, military, or GPS frequency ranges — the kind of transmissions that could indicate interference, unauthorized equipment, or a compliance issue. Security engineers and compliance teams use it to quickly audit RF survey data without having to memorize hundreds of frequency band regulations.
<!-- cognis:layman:end -->

## Upstream

Forks / wraps **https://github.com/gnuradio/gnuradio**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- Band-plan validator using FCC §2.106 public data
- GPS L1/L2 interference detector (critical infra)
- Federal/DoD-band transmission flagger
- CSV ingest from any SDR survey tool

<!-- cognis:domains:start -->
## Domains

**Primary domain:** Intelligence & OSINT  ·  **JTF MERIDIAN division:** NULLBYTE · BLACK CELL

**Topics:** `cognis` `osint` `intelligence` `recon`

Part of the **Cognis Neural Suite** — 300+ source-available tools organized across 12 domains under the JTF MERIDIAN command structure. See the [suite on GitHub](https://github.com/cognis-digital) and [jtf-meridian](https://github.com/cognis-digital/jtf-meridian) for how the pieces fit together.
<!-- cognis:domains:end -->

<!-- cognis:install:start -->
## Install

`sigsurvey-rf` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/sigsurvey-rf/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/sigsurvey-rf/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/sigsurvey-rf.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/sigsurvey-rf.git"  # uv
pip install "git+https://github.com/cognis-digital/sigsurvey-rf.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/sigsurvey-rf.git
cd sigsurvey-rf && pip install .
```

Then run:
```sh
sigsurvey-rf --help
```
<!-- cognis:install:end -->

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
    pip install "git+https://github.com/cognis-digital/sigsurvey-rf.git"
    sigsurvey-rf . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-4%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 4 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : sigsurvey-rf 0.1.0
package      : sigsurvey_rf
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
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
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m sigsurvey_rf --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>

