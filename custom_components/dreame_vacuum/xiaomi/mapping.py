"""MIoT maps and value conversion for Xiaomi vacuum models."""

from __future__ import annotations

from typing import Final

from .b106eu import S12, T12
from .b108gl import S20_PLUS
from .b112 import E10
from .b112bk import E10C
from .b112gl import E12
from .c101eu import X20
from .c108 import E5
from .d102gl import X20_PRO
from .d106gl import S20
from .d109gl import X20_MAX
from .e101gb import S40C
from .model import (
    MODEL_E5,
    MODEL_E10,
    MODEL_E10C,
    MODEL_E12,
    MODEL_H40,
    MODEL_H50,
    MODEL_H50_PRO,
    MODEL_H50_PRO_ROLLER,
    MODEL_H50_ROLLER,
    MODEL_MIJIA_5_PRO,
    MODEL_MIJIA_5C,
    MODEL_MIJIA_7C,
    MODEL_MIJIA_M40_S,
    MODEL_MIJIA_ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_5,
    MODEL_ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_6_MAX,
    MODEL_ROBOT_VACUUM_6_PRO,
    MODEL_S12,
    MODEL_S20,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_S60,
    MODEL_S60_PLUS,
    MODEL_T12,
    MODEL_X20,
    MODEL_X20_MAX,
    MODEL_X20_PRO,
    XiaomiModel,
)
from .ov21cn import MIJIA_5_PRO
from .ov21gl import ROBOT_VACUUM_5_PRO
from .ov31cn import MIJIA_M40_S
from .ov31gl import ROBOT_VACUUM_5
from .ov42cn import MIJIA_5C
from .ov42gl import H50_PRO
from .ov43gb import H50
from .ov51gl import H40
from .ov71gl import S40_PRO
from .ov81gl import S40
from .pv11gl import ROBOT_VACUUM_6_MAX
from .pv21gl import ROBOT_VACUUM_6_PRO
from .pv32cn import MIJIA_ROBOT_VACUUM_6
from .pv32gl import ROBOT_VACUUM_6
from .pv51gl import S60_PLUS
from .pv81gl import S60
from .qv41cn import MIJIA_7C
from .qv41gl import H50_PRO_ROLLER
from .qv42gl import H50_ROLLER

_FAMILIES: Final[dict[str, XiaomiModel]] = {
    MODEL_S20_PLUS: S20_PLUS,
    MODEL_X20_MAX: X20_MAX,
    MODEL_X20_PRO: X20_PRO,
    MODEL_ROBOT_VACUUM_5: ROBOT_VACUUM_5,
    MODEL_ROBOT_VACUUM_5_PRO: ROBOT_VACUUM_5_PRO,
    MODEL_ROBOT_VACUUM_6: ROBOT_VACUUM_6,
    MODEL_ROBOT_VACUUM_6_MAX: ROBOT_VACUUM_6_MAX,
    MODEL_ROBOT_VACUUM_6_PRO: ROBOT_VACUUM_6_PRO,
    MODEL_S60_PLUS: S60_PLUS,
    MODEL_S60: S60,
    MODEL_S40: S40,
    MODEL_S40_PRO: S40_PRO,
    MODEL_S40C: S40C,
    MODEL_H40: H40,
    MODEL_H50: H50,
    MODEL_H50_PRO: H50_PRO,
    MODEL_H50_PRO_ROLLER: H50_PRO_ROLLER,
    MODEL_H50_ROLLER: H50_ROLLER,
    MODEL_E10: E10,
    MODEL_E12: E12,
    MODEL_E10C: E10C,
    MODEL_E5: E5,
    MODEL_S20: S20,
    MODEL_X20: X20,
    MODEL_S12: S12,
    MODEL_T12: T12,
    MODEL_MIJIA_ROBOT_VACUUM_6: MIJIA_ROBOT_VACUUM_6,
    MODEL_MIJIA_7C: MIJIA_7C,
    MODEL_MIJIA_M40_S: MIJIA_M40_S,
    MODEL_MIJIA_5_PRO: MIJIA_5_PRO,
    MODEL_MIJIA_5C: MIJIA_5C,
}


def resolve_family(model: str) -> XiaomiModel | None:
    """Return the Xiaomi codec for a supported model, otherwise None."""
    return _FAMILIES.get(model)
