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
) -> dict[int, int]:
    """Copy a shared wire map and apply one model's overrides."""
    merged = {int(wire): int(stored) for wire, stored in base.items()}
    if overrides:
        for wire, stored in overrides.items():
            merged[int(wire)] = int(stored)
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
_S40_CLASS_ONLY_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    boolean_switch("xiaomi_ai_cleaning", 2, 37),
    boolean_switch("xiaomi_mop_auto_lift", 2, 44),
    boolean_switch("xiaomi_sweep_ai_detection", 2, 45),
    boolean_switch("xiaomi_dirt_detection", 2, 46),
    boolean_switch("xiaomi_object_detection", 2, 47),
    boolean_switch("xiaomi_room_detection", 2, 48),
    boolean_switch("xiaomi_floor_material_detection", 2, 49),
    boolean_switch("xiaomi_defecation_detection", 2, 50),
    boolean_switch("xiaomi_liquid_dirt_detection", 2, 51),
    boolean_switch("xiaomi_edge_swing_tail_sweep", 2, 55),
    enum_select(
        "xiaomi_edge_sweep_frequency",
        2,
        68,
        _OUTSWING_FREQUENCY_OPTIONS,
    ),
    boolean_switch("xiaomi_ai_managed_cleaning", 2, 69),
    boolean_switch("xiaomi_real_scene_capture", 2, 93),
    boolean_switch("xiaomi_auto_night_fill_light", 2, 94),
    boolean_switch("xiaomi_ai_wake_up", 2, 95),
)

S40_CLASS_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
    *HAIR_CUTTING_CONTROLS,
    *_S40_CLASS_ONLY_CONTROLS,
)

# H50 Pro and Robot Vacuum 5 Pro both publish this. The S40 spec does not.
SOLID_DIRT_DETECTION: Final = boolean_switch("xiaomi_solid_dirt_detection", 2, 52)

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
