from __future__ import annotations

import sys

from cognis_mil import make_cli

from . import __version__
from .core import scan


def main() -> int:
    """Entry point. Returns an exit code; never raises to the shell."""
    try:
        make_cli("sigsurvey-rf", scan, version=__version__)
    except SystemExit as exc:
        # make_cli calls sys.exit() itself; propagate its code cleanly.
        return int(exc.code) if exc.code is not None else 0
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"sigsurvey-rf: error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
