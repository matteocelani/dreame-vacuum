"""Every Xiaomi address must match the bundled MIoT spec, including inherited defaults."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumActionMapping,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
)
from custom_components.dreame_vacuum.xiaomi import (
    MODEL_H50_PRO,
    MODEL_ROBOT_VACUUM_5_PRO,
    resolve_family,
)
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_H40,
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_S40C,
    MODEL_X20_MAX,
)

_SPECS = Path(__file__).parent / "specs"
_PROPERTY_TEXT = {
    MODEL_S20_PLUS: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Suction Level",
        "WATER_VOLUME": "Mop Water Output Level",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "WATER_TANK": "mop-status",
        "DND": "dnd-switch",
        "SCHEDULE": "order-clean",
        "CARPET_BOOST": "carpet-boost",
        "RELOCATION_STATUS": "status-extend",
        "RESUME_CLEANING": "sweep-break-switch",
        "FAULTS": "fault-index",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "MOP_PAD_TIME_LEFT": "Brush Left Time",
        "MOP_PAD_LEFT": "Brush Life Level",
    },
    MODEL_X20_MAX: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "DETERGENT_LEFT": "Detergent Left Level",
    },
    MODEL_ROBOT_VACUUM_5: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "TOTAL_CLEANED_AREA": "Statistical Clean Area",
        "CLEANING_COUNT": "Statistical Cleaning Times",
        "TOTAL_CLEANING_TIME": "Statistical Cleaning Duration",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
        "DETERGENT_LEFT": "Detergent Left Level",
        "DETERGENT_TIME_LEFT": "Detergent Left Time",
    },
    MODEL_S40_PRO: {
        "STATE": "Status",
        "ERROR": "Device Fault",
        "CLEANING_MODE": "Sweep Mop Type",
        "TASK_STATUS": "Sweep Type",
        "CLEANED_AREA": "Cleaning Area",
        "CLEANING_TIME": "Cleaning Time",
        "SUCTION_LEVEL": "Mode",
        "WATER_VOLUME": "Mop Water Output Level",
        "WATER_TANK": "Mop Status",
        "SCHEDULE": "Order Clean",
        "CARPET_BOOST": "Carpet Boost",
        "RESUME_CLEANING": "Sweep Break Switch",
        "RELOCATION_STATUS": "Location Status",
        "AUTO_DUST_COLLECTING": "Auto Dust Arrest",
        "AUTO_EMPTY_FREQUENCY": "Dust Arrest Frequency",
        "CLEANING_PROPERTIES": "Current Cleaning Config",
        "FAULTS": "Fault Ids",
        "CARPET_CLEANING": "Carpet Cleaning Method",
        "TOTAL_CLEANED_AREA": "Statistical Clean Area",
        "CLEANING_COUNT": "Statistical Cleaning Times",
        "TOTAL_CLEANING_TIME": "Statistical Cleaning Duration",
        "BATTERY_LEVEL": "Battery Level",
        "CHARGING_STATUS": "Charging State",
        "VOLUME": "Volume",
        "CHILD_LOCK": "Physical Control Locked",
        "MOP_PAD_LEFT": "Mop Life Level",
        "MOP_PAD_TIME_LEFT": "Mop Left Time",
        "DND": "No Disturb",
        "MAIN_BRUSH_LEFT": "Brush Life Level",
        "MAIN_BRUSH_TIME_LEFT": "Brush Left Time",
        "SIDE_BRUSH_LEFT": "Brush Life Level",
        "SIDE_BRUSH_TIME_LEFT": "Brush Left Time",
        "FILTER_LEFT": "Filter Life Level",
        "FILTER_TIME_LEFT": "Filter Left Time",
    },
}
_ACTION_TEXT = {
    MODEL_S20_PLUS: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "continue-sweep",
        "CHARGE": "Start Charge",
        "LOCATE": "find-vacuum",
        "START_CUSTOM": "start-custom-sweep",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_MOP_PAD": "Reset Brush Life",
    },
    MODEL_X20_MAX: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_DETERGENT": "Reset Detergent Management Level",
    },
    MODEL_ROBOT_VACUUM_5: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
        "RESET_DETERGENT": "Reset Detergent Management Level",
    },
    MODEL_S40_PRO: {
        "START": "Start Sweep",
        "STOP": "Stop Sweeping",
        "PAUSE": "Pause Sweeping",
        "RESUME": "Continue Sweep",
        "START_CUSTOM": "Start Custom Sweep",
        "START_AUTO_EMPTY": "Start Dust Arrest",
        "CHARGE": "Start Charge",
        "LOCATE": "Identify",
        "RESET_MOP_PAD": "Reset Mop Life",
        "RESET_MAIN_BRUSH": "Reset Brush Life",
        "RESET_SIDE_BRUSH": "Reset Brush Life",
        "RESET_FILTER": "Reset Filter Life",
    },
}
_PROPERTY_TEXT[MODEL_S40] = _PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5]
_ACTION_TEXT[MODEL_S40] = _ACTION_TEXT[MODEL_ROBOT_VACUUM_5]
_PROPERTY_TEXT[MODEL_H40] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_H40] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_S40C] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_S40C] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_H50_PRO] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_H50_PRO] = _ACTION_TEXT[MODEL_S40]
_PROPERTY_TEXT[MODEL_ROBOT_VACUUM_5_PRO] = _PROPERTY_TEXT[MODEL_S40]
_ACTION_TEXT[MODEL_ROBOT_VACUUM_5_PRO] = _ACTION_TEXT[MODEL_S40]
_SPEC_FILES = {
    MODEL_S20_PLUS: ("b108gl.json",),
    MODEL_X20_MAX: ("d109gl.json", "d109gl_v1.json"),
    MODEL_ROBOT_VACUUM_5: ("ov31gl.json", "ov31gl_v1.json"),
    MODEL_S40_PRO: ("ov71gl.json",),
    MODEL_S40: ("ov81gl.json",),
    MODEL_H40: ("ov51gl.json",),
    MODEL_S40C: ("e101gb.json",),
    MODEL_H50_PRO: ("ov42gl.json", "ov42gl_v1.json"),
    MODEL_ROBOT_VACUUM_5_PRO: ("ov21gl.json", "ov21gl_v1.json"),
}
_ABSENT_PROPERTIES = (
    "STATUS",
    "OFF_PEAK_CHARGING",
    "DND_START",
    "DND_END",
    "MAP_DATA",
    "OBJECT_NAME",
    "OLD_MAP_DATA",
    "MAP_LIST",
    "MULTI_FLOOR_MAP",
    "MAP_SAVING",
    "SILVER_ION_LEFT",
    "SILVER_ION_TIME_LEFT",
    "AUTO_EMPTY_STATUS",
    "DUST_COLLECTION",
)
_ABSENT_ACTIONS = (
    "PLAY_SOUND",
    "BACKUP_MAP",
    "REQUEST_MAP",
    "UPDATE_MAP_DATA",
    "WIFI_MAP",
    "RESET_SILVER_ION",
)


class _Capability:
    loaded = False


class _Device:
    def __init__(self) -> None:
        self.property_mapping = None
        self.action_mapping = None
        self._property_codec = None
        self._map_manager = None
        self._protocol = type("Protocol", (), {"property_transport": None})()
        self.host = ""
        self.token = ""
        self.capability = _Capability()


def _load(name: str) -> tuple[dict[tuple[int, int], str], dict[tuple[int, int], str]]:
    document = json.loads((_SPECS / name).read_text(encoding="utf-8"))
    properties: dict[tuple[int, int], str] = {}
    actions: dict[tuple[int, int], str] = {}
    for service in document["services"]:
        siid = service["iid"]
        for prop in service.get("properties") or []:
            properties[(siid, prop["iid"])] = prop.get("description") or ""
        for action in service.get("actions") or []:
            actions[(siid, action["iid"])] = action.get("description") or ""
    return properties, actions


def _charging_value(name: str, number: int) -> str:
    document = json.loads((_SPECS / name).read_text(encoding="utf-8"))
    for service in document["services"]:
        if service["iid"] != 3:
            continue
        for prop in service["properties"]:
            if prop["iid"] == 2:
                for item in prop["value-list"]:
                    if item["value"] == number:
                        return item["description"]
    raise AssertionError(name)


def test_charging_value_three_is_not_chargeable():
    for name in (
        "b108gl.json",
        "d109gl.json",
        "d109gl_v1.json",
        "ov31gl.json",
        "ov31gl_v1.json",
        "ov71gl.json",
        "ov81gl.json",
        "ov51gl.json",
        "e101gb.json",
        "ov42gl.json",
        "ov42gl_v1.json",
        "ov21gl.json",
        "ov21gl_v1.json",
    ):
        assert _charging_value(name, 3) == "Not Chargeable"
        assert _charging_value(name, 1) == "Charging"


def test_installed_addresses_match_the_spec_and_defaults_do_not_leak():
    for model, filenames in _SPEC_FILES.items():
        family = resolve_family(model)
        assert family is not None
        device = _Device()
        apply_family(device, family)
        assert set(device.property_mapping) == {
            DreameVacuumProperty[name] for name in _PROPERTY_TEXT[model]
        }
        assert set(device.action_mapping) == {
            DreameVacuumAction[name] for name in _ACTION_TEXT[model]
        }
        for prop in _ABSENT_PROPERTIES:
            assert DreameVacuumProperty[prop] not in device.property_mapping
        for action in _ABSENT_ACTIONS:
            assert DreameVacuumAction[action] not in device.action_mapping
        for filename in filenames:
            properties, actions = _load(filename)
            _assert_properties(device, properties, _PROPERTY_TEXT[model])
            _assert_actions(device, actions, _ACTION_TEXT[model])


def _assert_properties(
    device: _Device, spec: dict[tuple[int, int], str], expected: dict[str, str]
) -> None:
    owners = {
        (mapping["siid"], mapping["piid"]): prop.name
        for prop, mapping in device.property_mapping.items()
    }
    for prop, mapping in device.property_mapping.items():
        assert spec[(mapping["siid"], mapping["piid"])] == expected[prop.name]
    for prop, mapping in DreameVacuumPropertyMapping.items():
        pair = (mapping.get("siid"), mapping.get("piid"))
        if pair not in spec:
            continue
        owner = owners.get(pair)
        if owner is None:
            installed = device.property_mapping.get(prop)
            assert installed is None or (installed["siid"], installed["piid"]) != pair
            continue
        assert spec[pair] == expected[owner]


def _assert_actions(
    device: _Device, spec: dict[tuple[int, int], str], expected: dict[str, str]
) -> None:
    owners = {
        (mapping["siid"], mapping["aiid"]): action.name
        for action, mapping in device.action_mapping.items()
    }
    for action, mapping in device.action_mapping.items():
        assert spec[(mapping["siid"], mapping["aiid"])] == expected[action.name]
    for action, mapping in DreameVacuumActionMapping.items():
        pair = (mapping.get("siid"), mapping.get("aiid"))
        if pair not in spec:
            continue
        owner = owners.get(pair)
        if owner is None:
            installed = device.action_mapping.get(action)
            assert installed is None or (installed["siid"], installed["aiid"]) != pair
            continue
        assert spec[pair] == expected[owner]
