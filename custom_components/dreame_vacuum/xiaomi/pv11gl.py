"""Xiaomi Robot Vacuum 6 Max record composed from the station profile and roller."""

from __future__ import annotations

from enum import IntEnum
from typing import Final

from .model import MODEL_ROBOT_VACUUM_6_MAX, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    ENTER_CHECK_MODE,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    HOST_TANK_WITH_NOT_INSTALLED,
    MOP_TEMPERATURE,
    ROLLER_CLEANING_MODE,
    ROLLER_CONTROLS,
    S40_CLASS_CONTROLS,
    SELF_CHECK_RESULTS,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    STREAM_CONTROLS,
    SWEEP_DUST_ARREST,
    WORRY_FREE_THROUGH_BUTLER,
    ExtendedStationWireState,
    StoredState,
    compose_addresses,
    compose_codes,
    compose_controls,
    select_controls,
)


class _SummonWireState(IntEnum):
    """Status codes this spec adds after the extended station list."""

    SELF_CHECK = 25
    SUMMONING = 26
    SWEEP_SUMMONING = 27


# The Dreame cleaning-mode select would write mop-only, which this spec omits.
_OMITTED_PROPERTIES: Final = frozenset({"CLEANING_MODE"})

# These addresses are on the shared lists and are absent from this spec.
_OMITTED_CONTROLS: Final = frozenset(
    {
        "xiaomi_calibrate_imu",
        "xiaomi_dust_arrest_power",
        "xiaomi_start_cut_hair",
        "xiaomi_start_mop",
        "xiaomi_start_station_self_clean",
        "xiaomi_stop_cut_hair",
        "xiaomi_stop_station_self_clean",
    }
)

# The shell has no self-check state. Old code 25 would display as water check.
_UNKNOWN_SHELL_STATE: Final = -1

_DETECTION_KEYS: Final = (
    "xiaomi_mop_auto_lift",
    "xiaomi_sweep_ai_detection",
    "xiaomi_dirt_detection",
    "xiaomi_object_detection",
    "xiaomi_room_detection",
    "xiaomi_edge_sweep_frequency",
    "xiaomi_real_scene_capture",
    "xiaomi_auto_night_fill_light",
    "xiaomi_ai_wake_up",
)
_STREAM_KEYS: Final = (
    "xiaomi_flash_light",
    "xiaomi_video_recording_warnings",
    "xiaomi_stream_visible_to_shared_users",
    "xiaomi_stream_enabled",
    "xiaomi_stream_physical_lock",
)
_ADDED_CONTROLS: Final = (
    ROLLER_CLEANING_MODE,
    *select_controls(S40_CLASS_CONTROLS, _DETECTION_KEYS),
    SELF_CHECK_RESULTS,
    SWEEP_DUST_ARREST,
    *ROLLER_CONTROLS,
    *select_controls(STREAM_CONTROLS, _STREAM_KEYS),
    MOP_TEMPERATURE,
    ENTER_CHECK_MODE,
)

ROBOT_VACUUM_6_MAX: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_6_MAX,
    property_overrides=compose_addresses(
        STATION_PROPERTIES,
        compose_addresses(STATION_STATISTICS_PROPERTIES, DETERGENT_TIME_PROPERTIES),
        omitted=_OMITTED_PROPERTIES,
    ),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(
        EXTENDED_STATION_STATES,
        {
            int(_SummonWireState.SELF_CHECK): _UNKNOWN_SHELL_STATE,
            int(_SummonWireState.SUMMONING): int(StoredState.CLEAN_SUMMON),
            int(_SummonWireState.SWEEP_SUMMONING): int(StoredState.SWEEPING),
        },
        omitted=(
            int(ExtendedStationWireState.STATION_ASSISTING),
            int(ExtendedStationWireState.STATION_ASSISTED),
        ),
    ),
    task_by_wire=compose_codes(EXTENDED_STATION_TASKS),
    controls=compose_controls(
        EXTENDED_STATION_CONTROLS,
        _ADDED_CONTROLS,
        omitted=_OMITTED_CONTROLS,
        replaced={
            "xiaomi_host_tank": HOST_TANK_WITH_NOT_INSTALLED,
            "xiaomi_worry_free_mode": WORRY_FREE_THROUGH_BUTLER,
        },
    ),
)
