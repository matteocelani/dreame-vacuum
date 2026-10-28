"""Dreame capability lists stay put. Xiaomi flags come from mapped names."""

from __future__ import annotations

import base64
from dataclasses import replace
import json
from types import SimpleNamespace
import zlib

from custom_components.dreame_vacuum.dreame.const import DEVICE_INFO
from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumDeviceCapability,
    RobotType,
)
from custom_components.dreame_vacuum.xiaomi.mapping import resolve_family

_CATALOG = json.loads(
    zlib.decompress(base64.b64decode(DEVICE_INFO), zlib.MAX_WBITS | 32)
)
_DREAME_P2008 = (
    "lidar_navigation",
    "object_shift",
    "disable_sensor_cleaning",
    "sweep_with_mop",
)
_MIJIA_C102GL = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mopping_after_sweeping",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "mop_clean_frequency",
    "obstacles",
    "new_state",
    "mijia",
    "auto_emptying",
    "no_detergent",
    "custom_cleaning_mode",
)
_MOVA_R2430 = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mop_pad_lifting_plus",
    "mopping_after_sweeping",
    "fill_light",
    "hot_washing",
    "max_suction_power",
    "obstacle_image_crop",
    "uv_sterilization",
    "self_clean_frequency",
    "auto_empty_mode",
    "floor_material",
    "floor_material_edit",
    "floor_direction_cleaning",
    "segment_visibility",
    "large_particles_boost",
    "fluid_detection",
    "intensive_carpet_cleaning",
    "mopping_settings",
    "cleaning_route",
    "segment_slow_clean_route",
    "pet_furniture",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "clean_carpets_first",
    "saved_furnitures",
    "extended_furnitures",
    "furnitures_v2",
    "wetness",
    "wetness_level",
    "obstacles",
    "water_check",
    "auto_carpet_cleaning",
    "segment_mopping_settings",
    "max_suction_power_extended",
    "auto_recleaning",
    "auto_rewashing",
    "new_state",
    "camera_streaming",
    "stream_tx",
    "stream_ali",
    "video_dynamic_vendor",
    "video_during_cleaning",
    "pet_snapshot",
    "video_audio",
    "gen5",
    "cleangenius_mode",
    "side_reach",
    "water_temperature",
    "smart_mop_washing",
    "dnd_functions",
    "ramps",
    "virtual_tracks",
    "side_brush_carpet_rotate",
    "area_rotation",
    "dynamic_obstacle_cleaning",
    "auto_add_detergent",
    "carpet_cleanset_v2",
    "carpet_shape",
    "carpet_id",
    "auto_emptying",
    "disable_mop_consumable",
    "onboard_dirty_water_tank",
    "drying_time_v2",
    "cleaning_sequence_v2",
    "custom_drying_time",
    "walls_v3",
    "quick_map_recovery",
    "curtains",
    "dock_status",
    "skip_area",
    "custom_cleaning_mode",
    "walls",
)
_COPIED_XIAOMI_ROW = (
    "lidar_navigation",
    "mop_pad_lifting",
    "mopping_after_sweeping",
    "disable_sensor_cleaning",
    "auto_rename_segment",
    "mop_clean_frequency",
    "obstacles",
    "new_state",
    "mijia",
    "auto_emptying",
    "custom_cleaning_mode",
)
_S20_PLUS = (
    "dnd",
    "disable_sensor_cleaning",
    "mijia",
)
_X20_MAX = (
    "auto_empty_base",
    "dnd",
    "disable_sensor_cleaning",
    "detergent",
    "mijia",
    "auto_emptying",
)
_S40_PRO = (
    "auto_empty_base",
    "dnd",
    "disable_sensor_cleaning",
    "mijia",
    "auto_emptying",
)


def _load(model: str, codec: object | None) -> DreameVacuumDeviceCapability:
    device = SimpleNamespace(
        info=SimpleNamespace(model=model, version=1),
        get_property=lambda _prop: None,
        _property_codec=codec,
        _map_manager=None,
        status=SimpleNamespace(
            current_segments=None,
            current_map=None,
            selected_map=None,
            fill_light=None,
        ),
    )
    capability = DreameVacuumDeviceCapability(device)
    capability.load(_CATALOG)
    return capability


def test_dreame_and_mijia_capability_lists_are_unchanged():
    assert resolve_family("xiaomi.vacuum.c102gl") is None
    assert resolve_family("dreame.vacuum.p2008") is None
    p2008 = _load("dreame.vacuum.p2008", None)
    c102gl = _load("xiaomi.vacuum.c102gl", None)
    mova = _load("mova.vacuum.r2430", None)
    assert tuple(p2008.list) == _DREAME_P2008
    assert tuple(c102gl.list) == _MIJIA_C102GL
    assert tuple(mova.list) == _MOVA_R2430
    assert p2008.robot_type is RobotType.LIDAR
    assert c102gl.self_wash_base is False
    assert c102gl.lidar_navigation is True


def test_catalog_row_stays_until_the_xiaomi_codec_is_installed():
    for model in (
        "xiaomi.vacuum.b108gl",
        "xiaomi.vacuum.d109gl",
        "xiaomi.vacuum.ov31gl",
        "xiaomi.vacuum.ov71gl",
        "xiaomi.vacuum.ov81gl",
    ):
        copied = _load(model, None)
        assert tuple(copied.list) == _COPIED_XIAOMI_ROW
        assert copied.self_wash_base is False
        assert copied.mop_pad_lifting is True


def test_s20_plus_and_x20_max_use_the_xiaomi_base():
    s20 = _load("xiaomi.vacuum.b108gl", resolve_family("xiaomi.vacuum.b108gl"))
    x20 = _load("xiaomi.vacuum.d109gl", resolve_family("xiaomi.vacuum.d109gl"))
    vacuum_5 = _load("xiaomi.vacuum.ov31gl", resolve_family("xiaomi.vacuum.ov31gl"))
    s40_pro = _load("xiaomi.vacuum.ov71gl", resolve_family("xiaomi.vacuum.ov71gl"))
    s40 = _load("xiaomi.vacuum.ov81gl", resolve_family("xiaomi.vacuum.ov81gl"))
    assert tuple(s20.list) == _S20_PLUS
    assert tuple(x20.list) == _X20_MAX
    assert tuple(vacuum_5.list) == _X20_MAX
    assert tuple(s40_pro.list) == _S40_PRO
    assert tuple(s40.list) == _X20_MAX
    for capability in (s20, x20, vacuum_5, s40_pro, s40):
        assert capability.self_wash_base is False
        assert capability.station_cleaning is False
        assert capability.lidar_navigation is False
        assert capability.mop_pad_lifting is False
        assert capability.new_state is False
        assert capability.obstacles is False
        assert capability.carpet_recognition is False
        assert capability.wifi_map is False
        assert capability.backup_map is False
        assert capability.drainage is False
        assert capability.robot_type is RobotType.LIDAR
        assert capability.mijia is True
        assert capability.dnd is True
    assert s20.auto_empty_base is False
    assert s20.auto_emptying is False
    assert s20.detergent is False
    assert x20.auto_empty_base is True
    assert x20.auto_emptying is True
    assert x20.auto_empty_mode is False
    assert x20.detergent is True
    assert vacuum_5.auto_empty_base is True
    assert vacuum_5.auto_emptying is True
    assert vacuum_5.detergent is True
    assert vacuum_5.self_wash_base is False
    assert vacuum_5.lidar_navigation is False
    assert s40_pro.auto_empty_base is True
    assert s40_pro.auto_emptying is True
    assert s40_pro.detergent is False
    assert s40_pro.self_wash_base is False
    assert s40_pro.lidar_navigation is False
    assert s40.auto_empty_base is True
    assert s40.auto_emptying is True
    assert s40.detergent is True
    assert s40.self_wash_base is False
    assert s40.lidar_navigation is False


def test_a_mapped_wash_base_or_map_turns_only_that_flag_on():
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    wash = replace(
        family,
        property_overrides={
            **family.property_overrides,
            "SELF_WASH_BASE_STATUS": {"siid": 99, "piid": 1},
        },
    )
    washed = _load("xiaomi.vacuum.b108gl", wash)
    assert washed.self_wash_base is True
    assert washed.station_cleaning is False
    assert washed.robot_type is RobotType.MOPPING

    mapped = replace(
        family,
        property_overrides={
            **family.property_overrides,
            "MAP_DATA": {"siid": 99, "piid": 2},
            "SENSOR_DIRTY_LEFT": {"siid": 99, "piid": 3},
        },
    )
    sensor = _load("xiaomi.vacuum.b108gl", mapped)
    assert sensor.lidar_navigation is True
    assert sensor.disable_sensor_cleaning is False
    assert sensor.self_wash_base is False


def test_apply_family_replaces_flags_when_the_capability_is_already_loaded():
    capability = _load("xiaomi.vacuum.b108gl", None)
    assert capability.mop_pad_lifting is True
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    device = SimpleNamespace(
        property_mapping=None,
        action_mapping=None,
        _property_codec=None,
        _map_manager=None,
        _protocol=SimpleNamespace(property_transport=None),
        host="",
        token="",
        capability=capability,
    )
    apply_family(device, family)
    assert capability.mop_pad_lifting is False
    assert capability.self_wash_base is False
    assert tuple(capability.list) == _S20_PLUS


def test_each_extra_mapped_name_turns_on_its_flag():
    """Names outside the three models still derive the flag the shell expects."""
    family = resolve_family("xiaomi.vacuum.b108gl")
    assert family is not None
    cases = (
        ("DND_TASK", "property", "dnd_task"),
        ("CARPET_RECOGNITION", "property", "carpet_recognition"),
        ("WASHBOARD_CLEANING_STATUS", "property", "station_cleaning"),
        ("DRAINAGE_STATUS", "property", "drainage"),
        ("OFF_PEAK_CHARGING", "property", "off_peak_charging"),
        ("WIFI_MAP", "property", "wifi_map"),
        ("MAP_BACKUP_STATUS", "property", "backup_map"),
        ("MULTI_FLOOR_MAP", "property", "multi_floor_map"),
        ("BACKUP_MAP", "action", "backup_map"),
        ("START_WASHING", "action", "self_wash_base"),
    )
    for name, kind, flag in cases:
        if kind == "property":
            updated = replace(
                family,
                property_overrides={
                    **family.property_overrides,
                    name: {"siid": 99, "piid": 1},
                },
            )
        else:
            updated = replace(
                family,
                action_overrides={
                    **family.action_overrides,
                    name: {"siid": 99, "aiid": 1},
                },
            )
        capability = _load("xiaomi.vacuum.b108gl", updated)
        assert getattr(capability, flag) is True, name
