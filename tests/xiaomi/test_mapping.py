"""Xiaomi model identity and value conversion."""

from __future__ import annotations

from pathlib import Path
import re
from types import SimpleNamespace

from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumState,
    DreameVacuumTaskStatus,
)
from custom_components.dreame_vacuum.xiaomi import (
    control_keys,
    controls_of,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_X20_MAX,
)
from custom_components.dreame_vacuum.xiaomi.profile import (
    STATION_ACTIONS,
    STATION_PROPERTIES,
)

_TOKEN = "00" * 16


def test_resolve_family_returns_none_for_mijia_dreame_and_unknown_models():
    assert resolve_family("xiaomi.vacuum.c102gl") is None
    assert resolve_family("xiaomi.vacuum.c102cn") is None
    assert resolve_family("xiaomi.vacuum.d103cn") is None
    assert resolve_family("xiaomi.vacuum.d110ch") is None
    assert resolve_family("dreame.vacuum.r2228") is None
    assert resolve_family("") is None


def test_s20_plus_state_and_task_values_convert_to_dreame_codes():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.is_simple_cleaning_mode is True
    assert family.should_correct_docked_activity is True
    assert family.convert_incoming("STATE", 4) == DreameVacuumState.SWEEPING
    assert family.convert_incoming("STATE", "1") == DreameVacuumState.IDLE
    assert family.convert_incoming("STATE", 7) == DreameVacuumState.REMOTE_CONTROL
    assert family.convert_incoming("STATE", 99) == 99
    assert (
        family.convert_incoming("TASK_STATUS", 4)
        == DreameVacuumTaskStatus.ZONE_CLEANING
    )
    assert (
        family.convert_incoming("TASK_STATUS", 8)
        == DreameVacuumTaskStatus.SEGMENT_CLEANING
    )
    assert "STATUS" not in family.property_overrides
    assert family.property_overrides["STATE"] == {"siid": 2, "piid": 1}
    assert family.action_overrides["RESUME"] == {"siid": 6, "aiid": 1}
    assert "REQUEST_MAP" not in family.action_overrides
    assert family.property_overrides["CLEANING_MODE"] == {"siid": 2, "piid": 3}
    assert family.convert_incoming("CHARGING_STATUS", 3) == 2
    assert family.convert_incoming("CHARGING_STATUS", 1) == 1


def test_x20_max_state_and_actions_follow_its_spec():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    assert (
        family.convert_incoming("STATE", 16) == DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert family.convert_incoming("STATE", 7) == DreameVacuumState.RETURNING_TO_WASH
    assert family.convert_incoming("STATE", 15) == DreameVacuumState.ERROR
    assert (
        family.convert_incoming("TASK_STATUS", 3)
        == DreameVacuumTaskStatus.SPOT_CLEANING
    )
    assert family.property_overrides["STATE"] == {"siid": 2, "piid": 2}
    assert family.property_overrides["ERROR"] == {"siid": 2, "piid": 3}
    assert family.action_overrides["RESUME"] == {"siid": 2, "aiid": 8}
    assert family.action_overrides["START_AUTO_EMPTY"] == {"siid": 2, "aiid": 18}
    assert family.action_overrides["RESET_DETERGENT"] == {"siid": 18, "aiid": 1}
    assert "REQUEST_MAP" not in family.action_overrides
    assert "RESET_SILVER_ION" not in family.action_overrides
    assert "STATUS" not in family.property_overrides


def test_cleaning_mode_and_suction_shift_only_on_the_wire_edges():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.convert_incoming("CLEANING_MODE", 1) == 0
    assert family.convert_incoming("CLEANING_MODE", 0) == 0
    assert family.convert_incoming("SUCTION_LEVEL", "3") == 2
    assert family.convert_incoming("SUCTION_LEVEL", 2.0) == 1
    assert family.convert_outgoing("CLEANING_MODE", 0) == 1
    assert family.convert_outgoing("SUCTION_LEVEL", 2) == 3
    assert family.convert_outgoing("CLEANING_MODE", False) is False
    assert family.convert_outgoing("VOLUME", 4) == 4
    assert family.convert_outgoing("CLEANING_MODE", "1") == "1"
    assert family.convert_incoming("SCHEDULE", "1-2-3") == "1-2-3"
    assert family.convert_incoming("VOLUME", True) is True
    assert family.convert_incoming("VOLUME", {"raw": 1}) == {"raw": 1}


def test_task_status_comes_from_state_when_sweep_type_would_stay_set():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    sweeping = int(DreameVacuumState.SWEEPING)
    assert family.task_status_code(sweeping, 1) == int(DreameVacuumTaskStatus.COMPLETED)
    assert family.task_status_code(sweeping, 3) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert family.task_status_code(sweeping, None) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert family.task_status_code(int(DreameVacuumState.PAUSED), None) == int(
        DreameVacuumTaskStatus.AUTO_CLEANING_PAUSED
    )
    assert family.task_status_code(int(DreameVacuumState.ERROR), 2) == int(
        DreameVacuumTaskStatus.COMPLETED
    )
    assert family.task_status_code(None, None) == int(DreameVacuumTaskStatus.COMPLETED)


def test_robot_vacuum_5_composes_the_station_profile_and_extends_status():
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    x20 = resolve_family(MODEL_X20_MAX)
    assert vacuum_5 is not None
    assert x20 is not None
    shared = set(x20.property_overrides)
    assert shared <= set(vacuum_5.property_overrides)
    for name in shared:
        assert vacuum_5.property_overrides[name] == x20.property_overrides[name]
    assert vacuum_5.action_overrides == x20.action_overrides
    assert (
        vacuum_5.convert_incoming("STATE", 16) == DreameVacuumState.SWEEPING_AND_MOPPING
    )
    assert vacuum_5.convert_incoming("STATE", 22) == DreameVacuumState.WASHING
    assert (
        vacuum_5.convert_incoming("STATE", 23) == DreameVacuumState.CHARGING_COMPLETED
    )
    assert vacuum_5.convert_incoming("STATE", 24) == DreameVacuumState.RETURNING
    assert vacuum_5.convert_incoming("STATE", 25) == 25
    assert (
        vacuum_5.convert_incoming("TASK_STATUS", 10)
        == DreameVacuumTaskStatus.FAST_MAPPING
    )
    assert (
        vacuum_5.convert_incoming("TASK_STATUS", 11)
        == DreameVacuumTaskStatus.AUTO_CLEANING
    )
    assert vacuum_5.property_overrides["TOTAL_CLEANED_AREA"] == {"siid": 2, "piid": 85}
    assert vacuum_5.property_overrides["DETERGENT_TIME_LEFT"] == {"siid": 18, "piid": 4}
    assert "TOTAL_CLEANED_AREA" not in x20.property_overrides
    assert "REQUEST_MAP" not in vacuum_5.action_overrides
    assert "STATUS" not in vacuum_5.property_overrides
    assert x20.controls == ()
    assert resolve_family(MODEL_S20_PLUS).controls == ()
    assert vacuum_5.controls
    assert x20.property_overrides is not STATION_PROPERTIES
    assert x20.property_overrides["STATE"] is not STATION_PROPERTIES["STATE"]
    assert vacuum_5.property_overrides["STATE"] is not x20.property_overrides["STATE"]


def test_station_address_literals_are_declared_once():
    """X20 Max declares no addresses of its own. Robot Vacuum 5 adds four."""
    root = Path("custom_components/dreame_vacuum/xiaomi")
    d109 = (root / "d109gl.py").read_text(encoding="utf-8")
    ov31 = (root / "ov31gl.py").read_text(encoding="utf-8")
    profile = (root / "profile.py").read_text(encoding="utf-8")
    assert "siid" not in d109
    assert "aiid" not in d109
    additions = re.findall(r"\{\"siid\": \d+, \"piid\": \d+\}", ov31)
    assert additions == [
        '{"siid": 2, "piid": 85}',
        '{"siid": 2, "piid": 86}',
        '{"siid": 2, "piid": 87}',
        '{"siid": 18, "piid": 4}',
    ]
    assert "aiid" not in ov31
    for mapping in STATION_PROPERTIES.values():
        needle = f'{{"siid": {mapping["siid"]}, "piid": {mapping["piid"]}}}'
        assert needle in profile
        assert needle not in ov31
        assert needle not in d109
    for mapping in STATION_ACTIONS.values():
        needle = f'{{"siid": {mapping["siid"]}, "aiid": {mapping["aiid"]}}}'
        assert needle in profile
        assert needle not in ov31
        assert needle not in d109


def test_controls_of_ignores_devices_without_a_xiaomi_codec():
    assert controls_of(object()) == ()
    assert controls_of(SimpleNamespace(_property_codec=object())) == ()
    family = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert family is not None
    device = SimpleNamespace(_property_codec=family)
    assert controls_of(device) == family.controls
    assert "xiaomi_alarm" in control_keys(device, "switch")
    assert control_keys(device, "vacuum") == frozenset()
    assert control_keys(SimpleNamespace(), "switch") == frozenset()


def test_property_and_action_names_exist_on_the_dreame_enums():
    for model in (MODEL_S20_PLUS, MODEL_X20_MAX, MODEL_ROBOT_VACUUM_5):
        family = resolve_family(model)
        assert family is not None
        for name in family.property_overrides:
            DreameVacuumProperty[name]
        for name in family.action_overrides:
            DreameVacuumAction[name]


def test_build_property_transport_skips_cloud_fallback_cases():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    assert family.build_property_transport("", _TOKEN) is None
    assert family.build_property_transport("127.0.0.1", "zz") is None
    transport = family.build_property_transport("127.0.0.1", _TOKEN)
    assert transport is not None
    assert "127.0.0.1" not in repr(transport)
    assert _TOKEN not in repr(transport)
