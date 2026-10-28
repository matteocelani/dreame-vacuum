"""MIoT maps and value conversion for Xiaomi vacuum models."""

from __future__ import annotations

from typing import Final

from .b108gl import S20_PLUS
from .d109gl import X20_MAX
from .model import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_X20_MAX,
    XiaomiModel,
)
from .ov31gl import ROBOT_VACUUM_5

_FAMILIES: Final[dict[str, XiaomiModel]] = {
    MODEL_S20_PLUS: S20_PLUS,
    MODEL_X20_MAX: X20_MAX,
    MODEL_ROBOT_VACUUM_5: ROBOT_VACUUM_5,
}


def resolve_family(model: str) -> XiaomiModel | None:
    """Return the Xiaomi codec for a supported model, otherwise None."""
    return _FAMILIES.get(model)
