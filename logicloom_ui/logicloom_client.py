"""Load LogicGateSimplifier from installed package or local logicloom_core."""

from __future__ import annotations

from pathlib import Path
import sys


def _load_logicloom():
    """Import LogicGateSimplifier from logicloom; add logicloom_core to path if needed."""
    try:
        from logicloom import LogicGateSimplifier
    except ImportError as exc:
        repo_root = Path(__file__).resolve().parents[1]
        local_pkg = repo_root / "logicloom_core"
        if local_pkg.exists():
            sys.path.insert(0, str(local_pkg))
            try:
                from logicloom import LogicGateSimplifier
            except ImportError:
                raise ImportError(
                    "LogicLoom package not found. Install 'logicloom' or "
                    "ensure 'logicloom_core' is available."
                ) from exc
            else:
                return LogicGateSimplifier
        raise ImportError(
            "LogicLoom package not found. Install 'logicloom' or "
            "ensure 'logicloom_core' is available."
        ) from exc
    else:
        return LogicGateSimplifier


LogicGateSimplifier = _load_logicloom()
