"""Xiaomi Robot Vacuum 5 Pro record composed from the extended station profile."""

from __future__ import annotations

from typing import Final

from .controls import action_button, binary_reading, boolean_switch, enum_select
from .model import MODEL_ROBOT_VACUUM_5_PRO, XiaomiModel
from .profile import (
    DETERGENT_TIME_PROPERTIES,
    EXTENDED_STATION_CONTROLS,
    EXTENDED_STATION_STATES,
    EXTENDED_STATION_TASKS,
    S40_CLASS_CONTROLS,
    SOLID_DIRT_DETECTION,
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    compose_addresses,
    compose_codes,
    compose_controls,
    control_with_options,
)

_STREAM_SERVICE: Final = 21
_FLASH_LIGHT_PROPERTY: Final = 2
_PET_SNAPS_PROPERTY: Final = 3
_VIDEO_WARNING_PROPERTY: Final = 4
_SHARED_USERS_PROPERTY: Final = 5
_STREAM_ENABLED_PROPERTY: Final = 6
_STREAM_LOCK_PROPERTY: Final = 8
_FIND_PET_ACTION: Final = 3

# This spec names value 0 Silent and value 2 Standard. The shared list does not.
_WORRY_FREE_MODE: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (0, "silent"),
        (1, "deep_clean"),
        (2, "standard"),
        (3, "butler"),
        (4, "pet"),
    ),
)

# Camera cruise and pet finding are published only by this spec.
_STREAM_CONTROLS: Final = (
    enum_select(
        "xiaomi_flash_light",
        _STREAM_SERVICE,
        _FLASH_LIGHT_PROPERTY,
        (
            (0, "auto"),
            (1, "open"),
            (2, "close"),
        ),
    ),
    boolean_switch("xiaomi_pet_snaps", _STREAM_SERVICE, _PET_SNAPS_PROPERTY),
    enum_select(
        "xiaomi_video_recording_warnings",
        _STREAM_SERVICE,
        _VIDEO_WARNING_PROPERTY,
        (
            (0, "voice"),
            (1, "light"),
            (2, "strong_reminder"),
        ),
    ),
    boolean_switch(
        "xiaomi_stream_visible_to_shared_users",
        _STREAM_SERVICE,
        _SHARED_USERS_PROPERTY,
    ),
    boolean_switch("xiaomi_stream_enabled", _STREAM_SERVICE, _STREAM_ENABLED_PROPERTY),
    binary_reading(
        "xiaomi_stream_physical_lock", _STREAM_SERVICE, _STREAM_LOCK_PROPERTY
    ),
    action_button("xiaomi_find_pet", _STREAM_SERVICE, _FIND_PET_ACTION),
)

_ADDED_CONTROLS: Final = (SOLID_DIRT_DETECTION, *_STREAM_CONTROLS)

ROBOT_VACUUM_5_PRO: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_5_PRO,
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
        replaced={"xiaomi_worry_free_mode": _WORRY_FREE_MODE},
    ),
)
