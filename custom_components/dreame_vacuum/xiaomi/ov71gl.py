"""Xiaomi Robot Vacuum S40 Pro record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .controls import boolean_switch, enum_select
from .model import MODEL_S40_PRO, XiaomiModel
from .profile import (
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    compose_addresses,
    compose_codes,
    compose_controls,
)

# The spec has no detergent service, so those station addresses stay unmapped.
_OMITTED_PROPERTIES: Final = frozenset({"DETERGENT_LEFT"})
_OMITTED_ACTIONS: Final = frozenset({"RESET_DETERGENT"})
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_detergent_delivery",
        "xiaomi_detergent_level",
        "xiaomi_dust_arrest_power",
        "xiaomi_dust_bag_life",
        "xiaomi_dust_bag_time_left",
        "xiaomi_enable_mop_wash",
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
        "xiaomi_repeat_wash_mop",
        "xiaomi_reset_dust_bag",
        "xiaomi_start_cut_hair",
        "xiaomi_start_dry",
        "xiaomi_wash_water_temperature",
    }
)
_ADDED_CONTROLS: Final = (
    boolean_switch("xiaomi_cut_hair", 2, 63),
    enum_select(
        "xiaomi_cut_hair_frequency",
        2,
        64,
        (
            (1, "every_clean"),
            (2, "every_two_cleans"),
            (3, "every_three_cleans"),
            (4, "during_task"),
        ),
    ),
)

S40_PRO: Final = XiaomiModel(
    model=MODEL_S40_PRO,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        STATION_STATISTICS_PROPERTIES,
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS, omitted=_OMITTED_ACTIONS),
    state_by_wire=compose_codes(EXTENDED_STATION_STATES),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_OMITTED_CONTROLS,
    ),
)
