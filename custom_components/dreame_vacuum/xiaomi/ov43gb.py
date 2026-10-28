"""Xiaomi Robot Vacuum H50 record composed from the extended station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_H50, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    LIDAR_HARDWARE_CONTROLS,
    S40_CLASS_CONTROLS,
    SELF_CHECK_RESULTS,
    SOLID_DIRT_DETECTION,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    STREAM_CONTROLS,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)

# This spec lists drying time through 12 hours. The shared list stops at 4.
_DRYING_TIME: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_drying_time",
    (
        (1, "hours_2"),
        (2, "hours_3"),
        (3, "hours_4"),
        (4, "hours_5"),
        (5, "hours_6"),
        (6, "hours_7"),
        (7, "hours_8"),
        (8, "hours_9"),
        (9, "hours_10"),
        (10, "hours_11"),
        (11, "hours_12"),
    ),
)

_ADDED_CONTROLS: Final = (
    SOLID_DIRT_DETECTION,
    SELF_CHECK_RESULTS,
    *STREAM_CONTROLS,
)

H50: Final = XiaomiModel(
    model=MODEL_H50,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        S40_CLASS_CONTROLS + _ADDED_CONTROLS,
        omitted=LIDAR_HARDWARE_CONTROLS,
        replaced={"xiaomi_drying_time": _DRYING_TIME},
    ),
)
