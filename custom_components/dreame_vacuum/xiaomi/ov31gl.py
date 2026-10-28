"""Xiaomi Robot Vacuum 5 record composed from the station profile."""

from __future__ import annotations

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
from .model import MODEL_ROBOT_VACUUM_5, XiaomiModel
from .profile import (
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATES,
    STATION_TASKS,
    StationWireState,
    StoredState,
    StoredTask,
    compose_addresses,
    compose_codes,
)

# Old remote code. The shell rewrites it to the current remote state; 23 would become washing-paused.
_LEGACY_REMOTE_CONTROL: Final = 19


class _ExtraState(IntEnum):
    """Status codes ov31gl adds after the station list."""

    STATION_ASSISTING = 22
    STATION_ASSISTED = 23
    RETURNING_DURING_ASSIST = 24


class _ExtraTask(IntEnum):
    """Sweep-type codes ov31gl adds after the station list."""

    APPOINTMENT = 8
    LINKAGE = 9
    FAST_MAPPING = 10
    AI_HOSTING = 11


_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "TOTAL_CLEANED_AREA": {"siid": 2, "piid": 85},
    "CLEANING_COUNT": {"siid": 2, "piid": 86},
    "TOTAL_CLEANING_TIME": {"siid": 2, "piid": 87},
    "DETERGENT_TIME_LEFT": {"siid": 18, "piid": 4},
}

_STATES: Final[dict[int, int]] = compose_codes(
    STATION_STATES,
    {
        int(StationWireState.REMOTE): _LEGACY_REMOTE_CONTROL,
        int(_ExtraState.STATION_ASSISTING): int(StoredState.WASHING),
        int(_ExtraState.STATION_ASSISTED): int(StoredState.CHARGING_COMPLETED),
        int(_ExtraState.RETURNING_DURING_ASSIST): int(StoredState.RETURNING),
    },
)

_TASKS: Final[dict[int, int]] = compose_codes(
    STATION_TASKS,
    {
        int(_ExtraTask.APPOINTMENT): int(StoredTask.AUTO_CLEANING),
        int(_ExtraTask.LINKAGE): int(StoredTask.AUTO_CLEANING),
        int(_ExtraTask.FAST_MAPPING): int(StoredTask.FAST_MAPPING),
        int(_ExtraTask.AI_HOSTING): int(StoredTask.AUTO_CLEANING),
    },
)

_CONTROLS: Final[tuple[XiaomiControl, ...]] = (
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
        (
            (1, "seven_sweeps"),
            (2, "every_time"),
        ),
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

ROBOT_VACUUM_5: Final = XiaomiModel(
    model=MODEL_ROBOT_VACUUM_5,
    property_overrides=compose_addresses(STATION_PROPERTIES, _PROPERTIES),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=_STATES,
    task_by_wire=_TASKS,
    controls=_CONTROLS,
)
