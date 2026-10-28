"""Shared station addresses and controls that X20 Max-like Xiaomi models compose."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import replace
from enum import IntEnum
from typing import Final

from .controls import (
    XiaomiControl,
    action_button,
    binary_reading,
    boolean_switch,
    enum_select,
    enum_sensor,
    mapped_select,
    measurement,
    number_control,
    text_sensor,
)


class StoredState(IntEnum):
    """Dreame state codes stored after Xiaomi values are converted."""

    SWEEPING = 1
    IDLE = 2
    PAUSED = 3
    ERROR = 4
    RETURNING = 5
    CHARGING = 6
    MOPPING = 7
    DRYING = 8
    WASHING = 9
    RETURNING_TO_WASH = 10
    BUILDING = 11
    SWEEPING_AND_MOPPING = 12
    CHARGING_COMPLETED = 13
    UPGRADING = 14
    # Below 19, so the old state enum does not relabel clean-summon.
    CLEAN_SUMMON = 15
    WASHING_PAUSED = 21
    REMOTE_CONTROL = 23
    STATION_CLEANING = 30


class StoredTask(IntEnum):
    """Dreame task-status codes stored for Xiaomi models."""

    COMPLETED = 0
    AUTO_CLEANING = 1
    ZONE_CLEANING = 2
    SEGMENT_CLEANING = 3
    SPOT_CLEANING = 4
    FAST_MAPPING = 5
    AUTO_CLEANING_PAUSED = 6


class StationWireState(IntEnum):
    """Wire status codes shared by the X20 Max station spec."""

    IDLE = 1
    CHARGING = 2
    BREAK_CHARGING = 3
    SWEEPING = 4
    PAUSED = 5
    RETURNING = 6
    GO_WASH = 7
    REMOTE = 8
    CHARGED = 9
    BUILDING = 10
    UPDATING = 11
    MULTI_TASK_STATION = 12
    MULTI_TASK_RECHARGE = 13
    STATION_WORKING = 14
    ERROR = 15
    SWEEPING_AND_MOPPING = 16
    MOPPING = 17
    MAPPING_PAUSE = 18
    GO_CHARGE_BREAK = 19
    WASH_BREAK = 20
    GO_CHARGE_BUILDING = 21


class StationWireTask(IntEnum):
    """Wire sweep-type codes shared by the X20 Max station spec."""

    GLOBAL = 1
    ZONE = 2
    AREA = 3
    EDGE = 4
    CUSTOM = 5
    POINT = 6
    CUSTOM_AREA = 7


class ExtendedStationWireState(IntEnum):
    """Status codes the extended station spec adds after the X20 Max list."""

    STATION_ASSISTING = 22
    STATION_ASSISTED = 23
    RETURNING_DURING_ASSIST = 24


class SummonWireState(IntEnum):
    """Status codes the summon specs add after the extended station list."""

    SELF_CHECK = 25
    SUMMONING = 26
    SWEEP_SUMMONING = 27


class ExtendedStationWireTask(IntEnum):
    """Sweep-type codes the extended station spec adds after the X20 Max list."""

    APPOINTMENT = 8
    LINKAGE = 9
    FAST_MAPPING = 10
    AI_HOSTING = 11


def wire_map(pairs: tuple[tuple[IntEnum, IntEnum], ...]) -> dict[int, int]:
    """Build a wire-code map from named pairs."""
    return {int(wire): int(stored) for wire, stored in pairs}


def compose_addresses(
    base: Mapping[str, Mapping[str, int]],
    additions: Mapping[str, Mapping[str, int]] | None = None,
    omitted: Collection[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Copy a shared address table, drop omitted names, and apply additions."""
    merged = {name: dict(address) for name, address in base.items()}
    if omitted:
        for name in omitted:
            if name not in merged:
                raise KeyError(name)
            del merged[name]
    if not additions:
        return merged
    for name, address in additions.items():
        merged[name] = dict(address)
    return merged


def compose_codes(
    base: Mapping[int, int],
    overrides: Mapping[int, int] | None = None,
    omitted: Collection[int] | None = None,
) -> dict[int, int]:
    """Copy a shared wire map, apply overrides, and drop codes the spec omits."""
    merged = {int(wire): int(stored) for wire, stored in base.items()}
    if overrides:
        for wire, stored in overrides.items():
            merged[int(wire)] = int(stored)
    if omitted:
        for wire in omitted:
            key = int(wire)
            if key not in merged:
                raise KeyError(key)
            del merged[key]
    return merged


def compose_controls(
    base: tuple[XiaomiControl, ...],
    additions: tuple[XiaomiControl, ...] = (),
    omitted: Collection[str] | None = None,
    replaced: Mapping[str, XiaomiControl] | None = None,
) -> tuple[XiaomiControl, ...]:
    """Copy a control list, drop keys, swap replacements, and append additions."""
    skipped = set(omitted) if omitted else set()
    swaps = dict(replaced) if replaced else {}
    overlap = skipped & set(swaps)
    if overlap:
        raise KeyError(next(iter(overlap)))
    present = {control.key for control in base}
    for name in skipped | set(swaps):
        if name not in present:
            raise KeyError(name)
    kept = tuple(
        swaps.get(control.key, control)
        for control in base
        if control.key not in skipped
    )
    return kept + additions


def select_controls(
    controls: tuple[XiaomiControl, ...],
    keys: tuple[str, ...],
) -> tuple[XiaomiControl, ...]:
    """Return named controls from a shared tuple, in the requested order."""
    by_key = {control.key: control for control in controls}
    chosen: list[XiaomiControl] = []
    for key in keys:
        control = by_key.get(key)
        if control is None:
            raise KeyError(key)
        chosen.append(control)
    return tuple(chosen)


def control_with_options(
    controls: tuple[XiaomiControl, ...],
    key: str,
    options: tuple[tuple[int, str], ...],
) -> XiaomiControl:
    """Copy one shared control with the value-list a single model publishes."""
    for control in controls:
        if control.key == key:
            return replace(control, options=options)
    raise KeyError(key)


STATION_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 2},
    "ERROR": {"siid": 2, "piid": 3},
    "CLEANING_MODE": {"siid": 2, "piid": 4},
    "TASK_STATUS": {"siid": 2, "piid": 5},
    "CLEANED_AREA": {"siid": 2, "piid": 6},
    "CLEANING_TIME": {"siid": 2, "piid": 7},
    "SUCTION_LEVEL": {"siid": 2, "piid": 9},
    "WATER_VOLUME": {"siid": 2, "piid": 10},
    "WATER_TANK": {"siid": 2, "piid": 11},
    "SCHEDULE": {"siid": 2, "piid": 19},
    "CARPET_BOOST": {"siid": 2, "piid": 20},
    "RESUME_CLEANING": {"siid": 2, "piid": 23},
    "RELOCATION_STATUS": {"siid": 2, "piid": 26},
    "AUTO_DUST_COLLECTING": {"siid": 2, "piid": 32},
    "AUTO_EMPTY_FREQUENCY": {"siid": 2, "piid": 33},
    "CLEANING_PROPERTIES": {"siid": 2, "piid": 40},
    "FAULTS": {"siid": 2, "piid": 66},
    "CARPET_CLEANING": {"siid": 2, "piid": 73},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "CHARGING_STATUS": {"siid": 3, "piid": 2},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "MOP_PAD_LEFT": {"siid": 9, "piid": 1},
    "MOP_PAD_TIME_LEFT": {"siid": 9, "piid": 2},
    "DND": {"siid": 11, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 12, "piid": 1},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 12, "piid": 2},
    "SIDE_BRUSH_LEFT": {"siid": 13, "piid": 1},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 13, "piid": 2},
    "FILTER_LEFT": {"siid": 14, "piid": 1},
    "FILTER_TIME_LEFT": {"siid": 14, "piid": 2},
    "DETERGENT_LEFT": {"siid": 18, "piid": 1},
}

STATION_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 7},
    "RESUME": {"siid": 2, "aiid": 8},
    "START_CUSTOM": {"siid": 2, "aiid": 9},
    "START_AUTO_EMPTY": {"siid": 2, "aiid": 18},
    "CHARGE": {"siid": 3, "aiid": 1},
    "LOCATE": {"siid": 6, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 9, "aiid": 1},
    "RESET_MAIN_BRUSH": {"siid": 12, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 13, "aiid": 1},
    "RESET_FILTER": {"siid": 14, "aiid": 1},
    "RESET_DETERGENT": {"siid": 18, "aiid": 1},
}

STATION_STATES: Final[dict[int, int]] = wire_map(
    (
        (StationWireState.IDLE, StoredState.IDLE),
        (StationWireState.CHARGING, StoredState.CHARGING),
        (StationWireState.BREAK_CHARGING, StoredState.CHARGING),
        (StationWireState.SWEEPING, StoredState.SWEEPING),
        (StationWireState.PAUSED, StoredState.PAUSED),
        (StationWireState.RETURNING, StoredState.RETURNING),
        (StationWireState.GO_WASH, StoredState.RETURNING_TO_WASH),
        (StationWireState.REMOTE, StoredState.REMOTE_CONTROL),
        (StationWireState.CHARGED, StoredState.CHARGING_COMPLETED),
        (StationWireState.BUILDING, StoredState.BUILDING),
        (StationWireState.UPDATING, StoredState.UPGRADING),
        (StationWireState.MULTI_TASK_STATION, StoredState.STATION_CLEANING),
        (StationWireState.MULTI_TASK_RECHARGE, StoredState.CHARGING),
        (StationWireState.STATION_WORKING, StoredState.STATION_CLEANING),
        (StationWireState.ERROR, StoredState.ERROR),
        (StationWireState.SWEEPING_AND_MOPPING, StoredState.SWEEPING_AND_MOPPING),
        (StationWireState.MOPPING, StoredState.MOPPING),
        (StationWireState.MAPPING_PAUSE, StoredState.PAUSED),
        (StationWireState.GO_CHARGE_BREAK, StoredState.RETURNING),
        (StationWireState.WASH_BREAK, StoredState.RETURNING_TO_WASH),
        (StationWireState.GO_CHARGE_BUILDING, StoredState.BUILDING),
    )
)

STATION_TASKS: Final[dict[int, int]] = wire_map(
    (
        (StationWireTask.GLOBAL, StoredTask.AUTO_CLEANING),
        (StationWireTask.ZONE, StoredTask.ZONE_CLEANING),
        (StationWireTask.AREA, StoredTask.SPOT_CLEANING),
        (StationWireTask.EDGE, StoredTask.ZONE_CLEANING),
        (StationWireTask.CUSTOM, StoredTask.SEGMENT_CLEANING),
        (StationWireTask.POINT, StoredTask.SPOT_CLEANING),
        (StationWireTask.CUSTOM_AREA, StoredTask.ZONE_CLEANING),
    )
)

# The shell maps codes above 18 through the old state enum when new_state is off.
# 23 is washing-paused there, so remote stays on the old remote code 19.
_LEGACY_REMOTE_CONTROL: Final = 19
_OUTSWING_FREQUENCY_OPTIONS: Final[tuple[tuple[int, str], ...]] = (
    (1, "seven_sweeps"),
    (2, "every_time"),
)

STATION_STATISTICS_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "TOTAL_CLEANED_AREA": {"siid": 2, "piid": 85},
    "CLEANING_COUNT": {"siid": 2, "piid": 86},
    "TOTAL_CLEANING_TIME": {"siid": 2, "piid": 87},
}

DETERGENT_TIME_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "DETERGENT_TIME_LEFT": {"siid": 18, "piid": 4},
}

# Detergent service 18 is empty on the S60-class spec.
_S60_CLASS_OMITTED_PROPERTIES: Final[frozenset[str]] = frozenset({"DETERGENT_LEFT"})
_S60_CLASS_OMITTED_ACTIONS: Final[frozenset[str]] = frozenset({"RESET_DETERGENT"})
S60_CLASS_PROPERTIES: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_PROPERTIES,
    STATION_STATISTICS_PROPERTIES,
    omitted=_S60_CLASS_OMITTED_PROPERTIES,
)
S60_CLASS_ACTIONS: Final[dict[str, dict[str, int]]] = compose_addresses(
    STATION_ACTIONS,
    omitted=_S60_CLASS_OMITTED_ACTIONS,
)

EXTENDED_STATION_STATES: Final[dict[int, int]] = compose_codes(
    STATION_STATES,
    {
        int(StationWireState.REMOTE): _LEGACY_REMOTE_CONTROL,
        int(ExtendedStationWireState.STATION_ASSISTING): int(StoredState.WASHING),
        int(ExtendedStationWireState.STATION_ASSISTED): int(
            StoredState.CHARGING_COMPLETED
        ),
        int(ExtendedStationWireState.RETURNING_DURING_ASSIST): int(
            StoredState.RETURNING
        ),
    },
)

# Old code 25 is water check. Self-check has no shell state of its own.
_UNKNOWN_SHELL_STATE: Final = -1

SUMMON_STATES: Final[dict[int, int]] = {
    int(SummonWireState.SELF_CHECK): _UNKNOWN_SHELL_STATE,
    int(SummonWireState.SUMMONING): int(StoredState.CLEAN_SUMMON),
}

# Sweep-summon has no shell state of its own, so it stays sweeping.
SWEEP_SUMMON_STATES: Final[dict[int, int]] = {
    int(SummonWireState.SWEEP_SUMMONING): int(StoredState.SWEEPING),
}

# Status runs through sweep-summon 27 and keeps station assist 22 and 23.
S60_CLASS_STATES: Final[dict[int, int]] = compose_codes(
    EXTENDED_STATION_STATES,
    {**SUMMON_STATES, **SWEEP_SUMMON_STATES},
)

EXTENDED_STATION_TASKS: Final[dict[int, int]] = compose_codes(
    STATION_TASKS,
    {
        int(ExtendedStationWireTask.APPOINTMENT): int(StoredTask.AUTO_CLEANING),
        int(ExtendedStationWireTask.LINKAGE): int(StoredTask.AUTO_CLEANING),
        int(ExtendedStationWireTask.FAST_MAPPING): int(StoredTask.FAST_MAPPING),
        int(ExtendedStationWireTask.AI_HOSTING): int(StoredTask.AUTO_CLEANING),
    },
)

EXTENDED_STATION_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_alarm", 4, 1),
    boolean_switch("xiaomi_carpet_avoidance", 2, 21),
    boolean_switch("xiaomi_enable_mop_wash", 2, 28),
    boolean_switch("xiaomi_auto_mop_dry", 2, 34),
    boolean_switch("xiaomi_auto_water_change", 2, 35),
    boolean_switch("xiaomi_use_detergent", 2, 36),
    boolean_switch("xiaomi_exit_remote_dialog", 2, 38),
    boolean_switch("xiaomi_hot_water_wash", 2, 41),
    boolean_switch("xiaomi_detergent_self_delivery", 2, 59),
    boolean_switch("xiaomi_detergent_reminder", 2, 71),
    boolean_switch("xiaomi_carpet_deep_cleaning", 2, 76),
    boolean_switch("xiaomi_carpet_discriminate", 2, 77),
    boolean_switch("xiaomi_sweep_carpet_first", 2, 78),
    boolean_switch("xiaomi_mop_outer_swing", 2, 79),
    boolean_switch("xiaomi_brush_outswing", 2, 91),
    boolean_switch("xiaomi_repeat_wash_mop", 2, 92),
    boolean_switch("xiaomi_detergent_delivery", 18, 2),
    enum_select(
        "xiaomi_clean_times",
        2,
        8,
        (
            (1, "one_time"),
            (2, "two_time"),
            (3, "three_time"),
        ),
    ),
    enum_select(
        "xiaomi_mop_wash_frequency",
        2,
        29,
        (
            (0, "by_room"),
            (1, "by_area"),
            (2, "by_time"),
        ),
    ),
    enum_select(
        "xiaomi_wash_water_output",
        2,
        30,
        (
            (0, "deep"),
            (1, "daily"),
            (2, "save_water"),
        ),
    ),
    enum_select(
        "xiaomi_drying_time",
        2,
        31,
        (
            (1, "hours_2"),
            (2, "hours_3"),
            (3, "hours_4"),
        ),
    ),
    enum_select(
        "xiaomi_mop_water_no_tank",
        2,
        60,
        (
            (0, "daily"),
            (1, "deep"),
        ),
    ),
    enum_select(
        "xiaomi_mop_wash_area",
        2,
        61,
        (
            (0, "five_square_meters"),
            (1, "ten_square_meters"),
            (2, "eight_square_meters"),
            (3, "fifteen_square_meters"),
            (4, "twenty_square_meters"),
            (5, "twenty_five_square_meters"),
        ),
    ),
    enum_select(
        "xiaomi_sweep_route",
        2,
        74,
        (
            (1, "quick"),
            (2, "daily"),
            (3, "careful"),
        ),
    ),
    enum_select(
        "xiaomi_obstacle_strategy",
        2,
        75,
        (
            (0, "less_collisions"),
            (1, "high_coverage"),
        ),
    ),
    enum_select(
        "xiaomi_mop_swing_frequency",
        2,
        80,
        _OUTSWING_FREQUENCY_OPTIONS,
    ),
    enum_select(
        "xiaomi_dust_arrest_power",
        2,
        82,
        (
            (0, "silent"),
            (1, "normal"),
            (2, "strong"),
        ),
    ),
    enum_select(
        "xiaomi_worry_free_mode",
        2,
        83,
        (
            (0, "silent_clean"),
            (1, "deep_clean"),
            (2, "general"),
            (3, "butler"),
            (4, "pet"),
        ),
    ),
    enum_select(
        "xiaomi_wash_water_temperature",
        2,
        84,
        (
            (0, "ordinary"),
            (1, "warm"),
            (2, "hot"),
            (3, "smart"),
        ),
    ),
    enum_select(
        "xiaomi_detergent_level",
        18,
        3,
        (
            (0, "few"),
            (1, "standard"),
            (2, "many"),
            (3, "lots"),
        ),
    ),
    enum_select(
        "xiaomi_obstacle_crossing",
        20,
        9,
        (
            (0, "safe_mode"),
            (1, "extreme_mode"),
        ),
    ),
    mapped_select(
        "xiaomi_carpet_cleaning_method",
        "CARPET_CLEANING",
        (
            (0, "self_adaption"),
            (1, "avoid"),
            (2, "ignore"),
            (3, "span"),
        ),
    ),
    number_control("xiaomi_mop_wash_interval", 2, 81, 0, 255),
    measurement("xiaomi_last_clean_time", 2, 17, 0, 4294967295),
    measurement("xiaomi_drying_progress", 2, 88, 0, 100, "%"),
    measurement("xiaomi_cleaning_progress", 2, 89, 0, 100, "%"),
    measurement("xiaomi_dry_left_time", 2, 90, 0, 9999),
    measurement("xiaomi_voltage", 3, 3, 0, 65535),
    measurement("xiaomi_download_progress", 15, 4, 0, 100, "%"),
    measurement("xiaomi_dust_bag_life", 19, 1, 0, 100, "%"),
    measurement("xiaomi_dust_bag_time_left", 19, 2, 0, 9999),
    enum_sensor(
        "xiaomi_water_check_status",
        2,
        54,
        (
            (0, "uncheck"),
            (1, "checking"),
            (2, "check_success"),
            (3, "check_fail"),
        ),
    ),
    enum_sensor(
        "xiaomi_sweep_mop_status",
        2,
        96,
        (
            (0, "idle"),
            (1, "sweeping"),
            (2, "mopping"),
        ),
    ),
    enum_sensor(
        "xiaomi_sewage_tank",
        2,
        97,
        (
            (0, "not_full"),
            (1, "full"),
        ),
    ),
    enum_sensor(
        "xiaomi_station_water_level",
        2,
        98,
        (
            (0, "not_empty"),
            (1, "empty"),
        ),
    ),
    enum_sensor(
        "xiaomi_base_station_tank",
        2,
        100,
        (
            (0, "idle"),
            (1, "emptying"),
            (2, "emptying_completed"),
            (3, "emptying_failed"),
        ),
    ),
    enum_sensor(
        "xiaomi_host_tank",
        2,
        101,
        (
            (0, "idle"),
            (1, "emptying"),
            (2, "emptying_completed"),
            (3, "emptying_failed"),
        ),
    ),
    enum_sensor(
        "xiaomi_download_status",
        15,
        3,
        (
            (0, "not_downloaded"),
            (1, "downloading"),
            (2, "downloaded"),
            (3, "download_fail"),
            (4, "apply_success"),
            (5, "apply_fail"),
        ),
    ),
    enum_sensor(
        "xiaomi_laser_position",
        20,
        11,
        (
            (0, "bottom"),
            (1, "top"),
            (2, "lifting"),
            (3, "lowering"),
        ),
    ),
    text_sensor("xiaomi_base_station_status", 2, 18),
    text_sensor("xiaomi_notice", 2, 72),
    text_sensor("xiaomi_current_voice", 15, 2),
    binary_reading("xiaomi_sleep_status", 2, 25),
    binary_reading("xiaomi_auto_water_change_installed", 2, 62),
    binary_reading("xiaomi_current_child_lock", 5, 2),
    binary_reading("xiaomi_current_dnd", 11, 3),
    action_button("xiaomi_stop_and_charge", 2, 3),
    action_button("xiaomi_start_sweep", 2, 4),
    action_button("xiaomi_start_mop", 2, 5),
    action_button("xiaomi_start_sweep_mop", 2, 6),
    action_button("xiaomi_start_mop_wash", 2, 19),
    action_button("xiaomi_start_dry", 2, 20),
    action_button("xiaomi_start_eject", 2, 21),
    action_button("xiaomi_call_clean", 2, 22),
    action_button("xiaomi_try_listen", 2, 27),
    action_button("xiaomi_enter_remote", 2, 28),
    action_button("xiaomi_exit_remote", 2, 29),
    action_button("xiaomi_stop_mop_wash", 2, 31),
    action_button("xiaomi_stop_dry", 2, 32),
    action_button("xiaomi_back_to_wash", 2, 36),
    action_button("xiaomi_start_cut_hair", 2, 43),
    action_button("xiaomi_stop_cut_hair", 2, 44),
    action_button("xiaomi_start_water_check", 2, 45),
    action_button("xiaomi_cancel_water_check", 2, 46),
    action_button("xiaomi_start_station_cleaning", 2, 49),
    action_button("xiaomi_sweep_before_mop", 2, 50),
    action_button("xiaomi_stop_working", 2, 51),
    action_button("xiaomi_empty_station_tank", 2, 57),
    action_button("xiaomi_empty_host_tank", 2, 58),
    action_button("xiaomi_spot_clean", 2, 59),
    action_button("xiaomi_start_station_self_clean", 2, 63),
    action_button("xiaomi_stop_station_self_clean", 2, 64),
    action_button("xiaomi_calibrate_imu", 16, 1),
    action_button("xiaomi_reset_dust_bag", 19, 1),
)

# The shared list also publishes Pet.
WORRY_FREE_THROUGH_BUTLER: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_worry_free_mode",
    (
        (0, "silent_clean"),
        (1, "deep_clean"),
        (2, "general"),
        (3, "butler"),
    ),
)

# The shared list stops at emptying failed.
HOST_TANK_WITH_NOT_INSTALLED: Final = control_with_options(
    EXTENDED_STATION_CONTROLS,
    "xiaomi_host_tank",
    (
        (0, "idle"),
        (1, "emptying"),
        (2, "emptying_completed"),
        (3, "emptying_failed"),
        (4, "not_installed"),
    ),
)

HAIR_CUTTING_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
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

# Shared by the S40-class spec. H40 lacks detergent reminder 2.71, which stays
# on the extended list so that model omits xiaomi_detergent_reminder.
_SWEEP_AI_DETECTION: Final = boolean_switch("xiaomi_sweep_ai_detection", 2, 45)
_EDGE_SWEEP_FREQUENCY: Final = enum_select(
    "xiaomi_edge_sweep_frequency",
    2,
    68,
    _OUTSWING_FREQUENCY_OPTIONS,
)

# Robot Vacuum 6 publishes only these two from the S40-class camera list.
AI_CAMERA_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    _SWEEP_AI_DETECTION,
    _EDGE_SWEEP_FREQUENCY,
)

_S40_CLASS_ONLY_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_ai_cleaning", 2, 37),
    boolean_switch("xiaomi_mop_auto_lift", 2, 44),
    _SWEEP_AI_DETECTION,
    boolean_switch("xiaomi_dirt_detection", 2, 46),
    boolean_switch("xiaomi_object_detection", 2, 47),
    boolean_switch("xiaomi_room_detection", 2, 48),
    boolean_switch("xiaomi_floor_material_detection", 2, 49),
    boolean_switch("xiaomi_defecation_detection", 2, 50),
    boolean_switch("xiaomi_liquid_dirt_detection", 2, 51),
    boolean_switch("xiaomi_edge_swing_tail_sweep", 2, 55),
    _EDGE_SWEEP_FREQUENCY,
    boolean_switch("xiaomi_ai_managed_cleaning", 2, 69),
    boolean_switch("xiaomi_real_scene_capture", 2, 93),
    boolean_switch("xiaomi_auto_night_fill_light", 2, 94),
    boolean_switch("xiaomi_ai_wake_up", 2, 95),
)

S40_CLASS_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    *HAIR_CUTTING_CONTROLS,
    *_S40_CLASS_ONLY_CONTROLS,
)

# H50, H50 Pro, and Robot Vacuum 5 Pro publish this. The S40 spec does not.
SOLID_DIRT_DETECTION: Final = boolean_switch("xiaomi_solid_dirt_detection", 2, 52)

# Robot Vacuum 5 Pro publishes these. H50 and H50 Pro leave them unmapped.
LIDAR_HARDWARE_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_laser_position",
        "xiaomi_obstacle_crossing",
    }
)

_STREAM_SERVICE: Final = 21
_FLASH_LIGHT_PROPERTY: Final = 2
_PET_SNAPS_PROPERTY: Final = 3
_VIDEO_WARNING_PROPERTY: Final = 4
_SHARED_USERS_PROPERTY: Final = 5
_STREAM_ENABLED_PROPERTY: Final = 6
_STREAM_LOCK_PROPERTY: Final = 8
_FIND_PET_ACTION: Final = 3

# Robot Vacuum 5 Pro and H50 publish camera cruise and pet finding.
STREAM_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
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

_SELF_CHECK_SERVICE: Final = 22
_SELF_CHECK_RESULTS_PROPERTY: Final = 2

# H50 Pro and H50 publish this readable string in spec version 2.
SELF_CHECK_RESULTS: Final = text_sensor(
    "xiaomi_self_check_results",
    _SELF_CHECK_SERVICE,
    _SELF_CHECK_RESULTS_PROPERTY,
)

_VACUUM_SERVICE: Final = 2
_CLEANING_MODE_PROPERTY: Final = 4
_MOP_TEMPERATURE_PROPERTY: Final = 107

# The Dreame select would send mop-only, which these specs do not publish.
ROLLER_CLEANING_MODE: Final = enum_select(
    "xiaomi_cleaning_mode",
    _VACUUM_SERVICE,
    _CLEANING_MODE_PROPERTY,
    (
        (1, "sweeping"),
        (3, "sweeping_and_mopping"),
        (4, "mopping_after_sweeping"),
    ),
)

_ROLLER_SERVICE: Final = 24
_ROLLER_LIFE_PROPERTY: Final = 1
_ROLLER_TIME_PROPERTY: Final = 2
_ROLLER_OUTSWING_PROPERTY: Final = 3
_ROLLER_AUTO_WASH_PROPERTY: Final = 4
_RESET_ROLLER_ACTION: Final = 1
_START_ROLLER_WASH_ACTION: Final = 2
_STOP_ROLLER_WASH_ACTION: Final = 3

# Robot Vacuum 6 mops with a roller. It does not publish mop-pad life.
ROLLER_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    measurement(
        "xiaomi_roller_life",
        _ROLLER_SERVICE,
        _ROLLER_LIFE_PROPERTY,
        0,
        100,
        "%",
    ),
    measurement(
        "xiaomi_roller_time_left",
        _ROLLER_SERVICE,
        _ROLLER_TIME_PROPERTY,
        0,
        9999,
    ),
    boolean_switch(
        "xiaomi_roller_outswing",
        _ROLLER_SERVICE,
        _ROLLER_OUTSWING_PROPERTY,
    ),
    boolean_switch(
        "xiaomi_auto_wash_roller",
        _ROLLER_SERVICE,
        _ROLLER_AUTO_WASH_PROPERTY,
    ),
    action_button("xiaomi_reset_roller", _ROLLER_SERVICE, _RESET_ROLLER_ACTION),
    action_button(
        "xiaomi_start_roller_wash",
        _ROLLER_SERVICE,
        _START_ROLLER_WASH_ACTION,
    ),
    action_button(
        "xiaomi_stop_roller_wash",
        _ROLLER_SERVICE,
        _STOP_ROLLER_WASH_ACTION,
    ),
)

_CUSTOM_SERVICE: Final = 20
_SWEEP_DUST_ARREST_ACTION: Final = 9
_ENTER_CHECK_MODE_ACTION: Final = 11

# Dust collection during a clean. Start-dust-arrest remains the dock empty.
SWEEP_DUST_ARREST: Final = action_button(
    "xiaomi_sweep_dust_arrest",
    _CUSTOM_SERVICE,
    _SWEEP_DUST_ARREST_ACTION,
)

# A parameter-free self-check entry. The result string is a separate sensor.
ENTER_CHECK_MODE: Final = action_button(
    "xiaomi_enter_check_mode",
    _CUSTOM_SERVICE,
    _ENTER_CHECK_MODE_ACTION,
)

# Device mop-water temperature. It is not the per-room Dreame mop-temperature map.
MOP_TEMPERATURE: Final = enum_select(
    "xiaomi_mop_temperature",
    _VACUUM_SERVICE,
    _MOP_TEMPERATURE_PROPERTY,
    (
        (0, "normal"),
        (1, "warm"),
        (2, "hot"),
        (3, "smart"),
    ),
)

_CAMERA_ROLLER_DETECTION_KEYS: Final = (
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
_CAMERA_ROLLER_STREAM_KEYS: Final = (
    "xiaomi_flash_light",
    "xiaomi_video_recording_warnings",
    "xiaomi_stream_visible_to_shared_users",
    "xiaomi_stream_enabled",
    "xiaomi_stream_physical_lock",
)

# Robot Vacuum 6 Max and 6 Pro add this camera, stream, and roller set.
CAMERA_ROLLER_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    ROLLER_CLEANING_MODE,
    *select_controls(S40_CLASS_CONTROLS, _CAMERA_ROLLER_DETECTION_KEYS),
    SELF_CHECK_RESULTS,
    SWEEP_DUST_ARREST,
    *ROLLER_CONTROLS,
    *select_controls(STREAM_CONTROLS, _CAMERA_ROLLER_STREAM_KEYS),
    MOP_TEMPERATURE,
    ENTER_CHECK_MODE,
)

# These shared-list addresses are absent from both of those specs.
CAMERA_ROLLER_OMITTED_CONTROLS: Final[frozenset[str]] = frozenset(
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

_VIBRATION_MOP_PROPERTY: Final = 109

# Both S60 models publish a vibrating mop pad. It is not a roller wash switch.
VIBRATION_MOP: Final = boolean_switch(
    "xiaomi_vibration_mop",
    _VACUUM_SERVICE,
    _VIBRATION_MOP_PROPERTY,
)

# Pad-mop slice both S60 models publish. Wash, roller, and stream services are empty.
_S60_CLASS_CONTROL_KEYS: Final = (
    "xiaomi_alarm",
    "xiaomi_carpet_avoidance",
    "xiaomi_exit_remote_dialog",
    "xiaomi_carpet_deep_cleaning",
    "xiaomi_carpet_discriminate",
    "xiaomi_sweep_carpet_first",
    "xiaomi_clean_times",
    "xiaomi_sweep_route",
    "xiaomi_worry_free_mode",
    "xiaomi_carpet_cleaning_method",
    "xiaomi_last_clean_time",
    "xiaomi_cleaning_progress",
    "xiaomi_voltage",
    "xiaomi_download_progress",
    "xiaomi_sweep_mop_status",
    "xiaomi_download_status",
    "xiaomi_base_station_status",
    "xiaomi_notice",
    "xiaomi_current_voice",
    "xiaomi_sleep_status",
    "xiaomi_current_child_lock",
    "xiaomi_current_dnd",
    "xiaomi_stop_and_charge",
    "xiaomi_start_sweep",
    "xiaomi_start_mop",
    "xiaomi_start_sweep_mop",
    "xiaomi_try_listen",
    "xiaomi_enter_remote",
    "xiaomi_exit_remote",
    "xiaomi_sweep_before_mop",
    "xiaomi_stop_working",
    "xiaomi_calibrate_imu",
)
S60_CLASS_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    *select_controls(EXTENDED_STATION_CONTROLS, _S60_CLASS_CONTROL_KEYS),
    *select_controls(S40_CLASS_CONTROLS, ("xiaomi_edge_sweep_frequency",)),
    SELF_CHECK_RESULTS,
    VIBRATION_MOP,
)

# Extended-station controls whose addresses the S40-class spec does not publish.
S40_CLASS_OMITTED_CONTROLS: Final[frozenset[str]] = frozenset(
    {
        "xiaomi_carpet_deep_cleaning",
        "xiaomi_carpet_discriminate",
        "xiaomi_laser_position",
        "xiaomi_mop_outer_swing",
        "xiaomi_mop_swing_frequency",
        "xiaomi_mop_wash_frequency",
        "xiaomi_mop_wash_interval",
        "xiaomi_obstacle_crossing",
        "xiaomi_sweep_carpet_first",
    }
)
