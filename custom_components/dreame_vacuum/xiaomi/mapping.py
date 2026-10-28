"""MIoT maps and value conversion for Xiaomi vacuum models."""

from __future__ import annotations

from typing import Final

from .b108gl import S20_PLUS
from .d109gl import X20_MAX
from .e101gb import S40C
from .model import (
    MODEL_H40,
    MODEL_H50,
    MODEL_H50_PRO,
    MODEL_ROBOT_VACUUM_5,
    MODEL_ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
    XiaomiModel,
)
from .ov21gl import ROBOT_VACUUM_5_PRO
from .ov31gl import ROBOT_VACUUM_5
from .ov42gl import H50_PRO
from .ov43gb import H50
from .ov51gl import H40
from .ov71gl import S40_PRO
from .ov81gl import S40
from .pv32gl import ROBOT_VACUUM_6

_FAMILIES: Final[dict[str, XiaomiModel]] = {
    MODEL_S20_PLUS: S20_PLUS,
    MODEL_X20_MAX: X20_MAX,
    MODEL_ROBOT_VACUUM_5: ROBOT_VACUUM_5,
    MODEL_ROBOT_VACUUM_5_PRO: ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6: ROBOT_VACUUM_6,
    MODEL_S40: S40,
    MODEL_S40_PRO: S40_PRO,
    MODEL_S40C: S40C,
    MODEL_H40: H40,
    MODEL_H50: H50,
    MODEL_H50_PRO: H50_PRO,
}


def resolve_family(model: str) -> XiaomiModel | None:
    """Return the Xiaomi codec for a supported model, otherwise None."""
    return _FAMILIES.get(model)
