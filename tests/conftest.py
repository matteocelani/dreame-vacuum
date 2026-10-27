"""Import device-core modules without loading the Home Assistant shell."""

from __future__ import annotations

from pathlib import Path
import sys
import types

_ROOT = Path(__file__).resolve().parents[1]
_COMPONENT = _ROOT / "custom_components"
_PACKAGE = _COMPONENT / "dreame_vacuum"


def _install(name: str, path: Path) -> None:
    if name in sys.modules:
        return
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    module.__package__ = name
    sys.modules[name] = module


_install("custom_components", _COMPONENT)
_install("custom_components.dreame_vacuum", _PACKAGE)
_install("custom_components.dreame_vacuum.dreame", _PACKAGE / "dreame")
