"""Xiaomi Robot Vacuum H50 Pro record composed from the S40-class station profile."""

from __future__ import annotations

from typing import Final

from .controls import boolean_switch, text_sensor
from .model import MODEL_H50_PRO, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    S40_CLASS_CONTROLS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    compose_addresses,
    compose_codes,
    compose_controls,
)

_VACUUM_SERVICE: Final = 2
_SOLID_DIRT_PROPERTY: Final = 52
_SELF_CHECK_SERVICE: Final = 22
_SELF_CHECK_RESULTS_PROPERTY: Final = 2

# Published by this spec and absent from the S40-class spec.
_ADDED_CONTROLS: Final = (
    boolean_switch(
        "xiaomi_solid_dirt_detection", _VACUUM_SERVICE, _SOLID_DIRT_PROPERTY
    ),
    text_sensor(
        "xiaomi_self_check_results",
        _SELF_CHECK_SERVICE,
        _SELF_CHECK_RESULTS_PROPERTY,
    ),
)

# Laser position and obstacle crossing are not in this spec.
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
    }
)

H50_PRO: Final = XiaomiModel(
    model=MODEL_H50_PRO,
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
        omitted=_OMITTED_CONTROLS,
    ),
)
