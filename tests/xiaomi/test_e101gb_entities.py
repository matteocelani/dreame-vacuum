"""Home Assistant entities for xiaomi.vacuum.e101gb, the Robot Vacuum S40C."""

from __future__ import annotations

import contextlib
import sys
from typing import Final

from custom_components.dreame_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.controls import XiaomiControl
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_S40C,
    XiaomiModel,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.xiaomi.helpers import FakeMiio, release_device, traffic_outside_map

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

_TOKEN: Final = "00" * 16
_MAC: Final = "00:00:00:00:00:00"
_ENTITIES: Final = frozenset(
    {
        ("binary_sensor", "charging_state"),
        ("binary_sensor", "maintenance"),
        ("binary_sensor", "problem"),
        ("button", "reset_detergent"),
        ("button", "reset_filter"),
        ("button", "reset_main_brush"),
        ("button", "reset_mop_pad"),
        ("button", "reset_side_brush"),
        ("button", "start_auto_empty"),
        ("sensor", "firmware_version"),
        ("number", "volume"),
        ("select", "auto_empty_frequency"),
        ("select", "cleaning_mode"),
        ("select", "suction_level"),
        ("select", "water_volume"),
        ("sensor", "battery_level"),
        ("sensor", "charging_status"),
        ("sensor", "cleaned_area"),
        ("sensor", "detergent_left"),
        ("sensor", "detergent_time_left"),
        ("sensor", "cleaning_count"),
        ("sensor", "cleaning_time"),
        ("sensor", "error"),
        ("sensor", "filter_left"),
        ("sensor", "filter_time_left"),
        ("sensor", "main_brush_left"),
        ("sensor", "main_brush_time_left"),
        ("sensor", "mop_pad_left"),
        ("sensor", "mop_pad_time_left"),
        ("sensor", "relocation_status"),
        ("sensor", "side_brush_left"),
        ("sensor", "side_brush_time_left"),
        ("sensor", "state"),
        ("sensor", "task_status"),
        ("sensor", "total_cleaned_area"),
        ("sensor", "total_cleaning_time"),
        ("sensor", "water_tank"),
        ("switch", "auto_dust_collecting"),
        ("switch", "carpet_boost"),
        ("switch", "child_lock"),
        ("switch", "dnd"),
        ("switch", "resume_cleaning"),
        ("vacuum", "dreame_vacuum"),
    }
)
_COUNTER_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "BATTERY_LEVEL": (55, "55"),
    "CLEANED_AREA": (12, "12"),
    "CLEANING_TIME": (9, "9"),
    "CLEANING_COUNT": (4, "4"),
    "DETERGENT_LEFT": (40, "40"),
    "DETERGENT_TIME_LEFT": (6, "6"),
    "TOTAL_CLEANED_AREA": (30, "30"),
    "TOTAL_CLEANING_TIME": (15, "15"),
    "MAIN_BRUSH_LEFT": (80, "80"),
    "MAIN_BRUSH_TIME_LEFT": (70, "70"),
    "SIDE_BRUSH_LEFT": (81, "81"),
    "SIDE_BRUSH_TIME_LEFT": (71, "71"),
    "FILTER_LEFT": (82, "82"),
    "FILTER_TIME_LEFT": (72, "72"),
    "MOP_PAD_LEFT": (83, "83"),
    "MOP_PAD_TIME_LEFT": (73, "73"),
    "ERROR": (0, "no_error"),
    "RELOCATION_STATUS": (False, "located"),
    "WATER_TANK": (True, "installed"),
}
_STATUS_SAMPLES: Final[dict[str, tuple[object, str]]] = {
    "CHARGING_STATUS": (2, "not_charging"),
    "STATE": (1, "idle"),
    "TASK_STATUS": (1, "completed"),
}
_CONSUMABLE_LIFE: Final = (
    "MAIN_BRUSH_LEFT",
    "SIDE_BRUSH_LEFT",
    "FILTER_LEFT",
    "MOP_PAD_LEFT",
    "DETERGENT_LEFT",
)

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


async def test_home_assistant_entities_cover_every_exposed_control(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Drive every entity this model creates and keep traffic on the map."""
    del socket_enabled, integration_package
    version = sys.modules["custom_components.dreame_vacuum.dreame"].VERSION
    family = resolve_family(MODEL_S40C)
    assert family is not None
    with FakeMiio(MODEL_S40C) as fake:
        entry = _entry(hass, version)
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            keys = _registry_keys(hass, entry.entry_id)
            assert not any(domain == "time" for domain, _key in keys)
            expected = set(_ENTITIES)
            expected.update(
                (str(control.domain), control.key) for control in family.controls
            )
            assert keys == expected
            assert not any(domain == "camera" for domain, _key in keys)
            await _exercise_selects_switches_number_and_buttons(hass, fake, family)
            await _exercise_vacuum_states(hass, entry.entry_id, fake, family)
            await _exercise_sensors(hass, entry.entry_id, fake, family)
            await _exercise_binary_sensors(hass, entry.entry_id, fake, family)
            await _exercise_controls(hass, entry.entry_id, fake, family)
        finally:
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)
    _assert_traffic_is_mapped(fake, family)


def _entry(hass: HomeAssistant, version: int) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="S40C Sim",
        data={
            CONF_NAME: "S40C Sim",
            CONF_HOST: "127.0.0.1",
            CONF_TOKEN: _TOKEN,
            CONF_MAC: _MAC,
            CONF_ACCOUNT_TYPE: "mi",
        },
        options={
            CONF_PREFER_CLOUD: False,
            CONF_NOTIFY: False,
            CONF_VERSION: version,
        },
    )


def _registry_keys(hass: HomeAssistant, entry_id: str) -> set[tuple[str, str]]:
    registry = er.async_get(hass)
    keys: set[tuple[str, str]] = set()
    prefix = f"{_MAC}_"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        assert item.unique_id.startswith(prefix)
        keys.add((item.domain, item.unique_id.removeprefix(prefix)))
    return keys


def _entity_id(hass: HomeAssistant, entry_id: str, domain: str, key: str) -> str:
    registry = er.async_get(hass)
    unique_id = f"{_MAC}_{key}"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        if item.domain == domain and item.unique_id == unique_id:
            return item.entity_id
    raise AssertionError((domain, key))


def _state(hass: HomeAssistant, entry_id: str, domain: str, key: str) -> str:
    state = hass.states.get(_entity_id(hass, entry_id, domain, key))
    assert state is not None
    return state.state


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()


async def _exercise_selects_switches_number_and_buttons(
    hass: HomeAssistant, fake: FakeMiio, family: XiaomiModel
) -> None:
    entry_id = _config_entry_id(hass)
    await _select_each(hass, entry_id, "suction_level")
    await _select_each(hass, entry_id, "cleaning_mode")
    tank = family.property_overrides["WATER_TANK"]
    fake.set_value(tank["siid"], tank["piid"], True)
    await _refresh(hass, entry_id)
    await _select_each(hass, entry_id, "water_volume")
    await _select_each(hass, entry_id, "cleaning_mode")
    dust = family.property_overrides["AUTO_DUST_COLLECTING"]
    fake.set_value(dust["siid"], dust["piid"], 1)
    await _refresh(hass, entry_id)
    await _select_each(hass, entry_id, "auto_empty_frequency")
    for key in (
        "resume_cleaning",
        "carpet_boost",
        "child_lock",
        "dnd",
        "auto_dust_collecting",
    ):
        entity_id = _entity_id(hass, entry_id, "switch", key)
        for service in ("turn_on", "turn_off"):
            await hass.services.async_call(
                "switch",
                service,
                {"entity_id": entity_id},
                blocking=True,
            )
    volume_id = _entity_id(hass, entry_id, "number", "volume")
    for value in (0, 50, 100):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": volume_id, "value": value},
            blocking=True,
        )
    for key in (
        "reset_main_brush",
        "reset_side_brush",
        "reset_filter",
        "reset_mop_pad",
        "reset_detergent",
    ):
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": _entity_id(hass, entry_id, "button", key)},
            blocking=True,
        )
    empty_id = _entity_id(hass, entry_id, "button", "start_auto_empty")
    assert hass.states.get(empty_id).state == "unavailable"
    before = len(fake.actions)
    with contextlib.suppress(HomeAssistantError):
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": empty_id},
            blocking=True,
        )
    assert len(fake.actions) == before


async def _select_each(hass: HomeAssistant, entry_id: str, key: str) -> None:
    entity_id = _entity_id(hass, entry_id, "select", key)
    state = hass.states.get(entity_id)
    assert state is not None
    options = state.attributes["options"]
    assert options
    for option in options:
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": entity_id, "option": option},
            blocking=True,
        )


def _config_entry_id(hass: HomeAssistant) -> str:
    entry_ids = list(hass.data[DOMAIN])
    assert len(entry_ids) == 1
    return entry_ids[0]


async def _exercise_vacuum_states(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, family: XiaomiModel
) -> None:
    state = family.property_overrides["STATE"]
    charging = family.property_overrides["CHARGING_STATUS"]
    error = family.property_overrides["ERROR"]
    vacuum_id = _entity_id(hass, entry_id, "vacuum", "dreame_vacuum")

    async def show(
        wire: int, charging_wire: int, error_wire: int, expected: str
    ) -> None:
        fake.set_value(state["siid"], state["piid"], wire)
        fake.set_value(charging["siid"], charging["piid"], charging_wire)
        fake.set_value(error["siid"], error["piid"], error_wire)
        await _refresh(hass, entry_id)
        assert hass.states.get(vacuum_id).state == expected

    await show(1, 2, 0, "idle")
    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert hass.states.get(vacuum_id).state == "cleaning"
    await hass.services.async_call(
        "vacuum", "pause", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert hass.states.get(vacuum_id).state == "paused"
    await hass.services.async_call(
        "vacuum", "start", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert hass.states.get(vacuum_id).state == "cleaning"
    assert fake.actions[-1] == (
        family.action_overrides["RESUME"]["siid"],
        family.action_overrides["RESUME"]["aiid"],
    )
    await hass.services.async_call(
        "vacuum", "stop", {"entity_id": vacuum_id}, blocking=True
    )
    assert fake.actions[-1] == (
        family.action_overrides["STOP"]["siid"],
        family.action_overrides["STOP"]["aiid"],
    )
    await show(6, 2, 0, "returning")
    await hass.services.async_call(
        "vacuum", "return_to_base", {"entity_id": vacuum_id}, blocking=True
    )
    await _refresh(hass, entry_id)
    assert hass.states.get(vacuum_id).state == "docked"
    await show(2, 1, 0, "docked")
    await show(15, 2, 0, "error")
    await show(1, 2, 1, "error")
    await hass.services.async_call(
        "vacuum", "locate", {"entity_id": vacuum_id}, blocking=True
    )
    assert fake.actions[-1] == (
        family.action_overrides["LOCATE"]["siid"],
        family.action_overrides["LOCATE"]["aiid"],
    )


async def _show_sensors(
    hass: HomeAssistant,
    entry_id: str,
    fake: FakeMiio,
    family: XiaomiModel,
    samples: dict[str, tuple[object, str]],
) -> None:
    for name, (wire, _expected) in samples.items():
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], wire)
    await _refresh(hass, entry_id)
    for name, (_wire, expected) in samples.items():
        state = _state(hass, entry_id, "sensor", name.lower())
        assert expected in state, (name, state)


async def _exercise_sensors(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, family: XiaomiModel
) -> None:
    sensor_keys = {
        key for domain, key in _registry_keys(hass, entry_id) if domain == "sensor"
    }
    assert sensor_keys == {
        name.lower() for name in {**_COUNTER_SAMPLES, **_STATUS_SAMPLES}
    } | {"firmware_version"} | {
        control.key for control in family.controls if control.domain == "sensor"
    }
    await _show_sensors(hass, entry_id, fake, family, _COUNTER_SAMPLES)
    # Idle clears the current-job counters, so status is applied after them.
    await _show_sensors(hass, entry_id, fake, family, _STATUS_SAMPLES)
    # fw_ver "1.0_1" is stored as the integer after the underscore.
    firmware = _state(hass, entry_id, "sensor", "firmware_version")
    assert firmware == "1"


async def _exercise_binary_sensors(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, family: XiaomiModel
) -> None:
    binary_keys = {
        key
        for domain, key in _registry_keys(hass, entry_id)
        if domain == "binary_sensor"
    }
    assert binary_keys == {"charging_state", "problem", "maintenance"} | {
        control.key for control in family.controls if control.domain == "binary_sensor"
    }
    charging = family.property_overrides["CHARGING_STATUS"]
    battery = family.property_overrides["BATTERY_LEVEL"]
    error = family.property_overrides["ERROR"]
    fake.set_value(battery["siid"], battery["piid"], 90)
    fake.set_value(charging["siid"], charging["piid"], 1)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "charging_state") == "on"
    fake.set_value(charging["siid"], charging["piid"], 2)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "charging_state") == "off"
    fake.set_value(error["siid"], error["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "problem") == "off"
    fake.set_value(error["siid"], error["piid"], 1)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "problem") == "on"
    for name in _CONSUMABLE_LIFE:
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "on"
    for name in _CONSUMABLE_LIFE:
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], 80)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "off"
    brush = family.property_overrides["MAIN_BRUSH_LEFT"]
    fake.set_value(brush["siid"], brush["piid"], 0)
    await _refresh(hass, entry_id)
    assert _state(hass, entry_id, "binary_sensor", "maintenance") == "on"


async def _exercise_controls(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, family: XiaomiModel
) -> None:
    for control in family.controls:
        if control.domain == "switch":
            await _flip_switch(hass, entry_id, control.key)
        elif control.domain == "select":
            await _seed_select(hass, entry_id, fake, control)
            await _select_each(hass, entry_id, control.key)
        elif control.domain == "number":
            await _set_number_samples(hass, entry_id, control)
        elif control.domain == "button":
            await hass.services.async_call(
                "button",
                "press",
                {"entity_id": _entity_id(hass, entry_id, "button", control.key)},
                blocking=True,
            )
            assert fake.actions[-1] == (control.siid, control.aiid)
            assert fake.action_inputs[-1] == []
        elif control.domain == "sensor":
            await _show_control_sensor(hass, entry_id, fake, control)
        elif control.domain == "binary_sensor":
            await _show_binary_control(hass, entry_id, fake, control)


async def _flip_switch(hass: HomeAssistant, entry_id: str, key: str) -> None:
    entity_id = _entity_id(hass, entry_id, "switch", key)
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert hass.states.get(entity_id).state == "on"
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert hass.states.get(entity_id).state == "off"


async def _seed_select(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    value = control.options[0][0]
    if control.siid is not None:
        fake.set_value(control.siid, control.piid, value)
        await _refresh(hass, entry_id)
    state = hass.states.get(_entity_id(hass, entry_id, "select", control.key))
    assert state is not None
    assert state.state != "unavailable"


async def _set_number_samples(
    hass: HomeAssistant, entry_id: str, control: XiaomiControl
) -> None:
    entity_id = _entity_id(hass, entry_id, "number", control.key)
    middle = control.minimum + ((control.maximum - control.minimum) // 2)
    for value in (control.minimum, middle, control.maximum):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": value},
            blocking=True,
        )
        assert hass.states.get(entity_id).state == str(value)


async def _show_control_sensor(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    entity_id = _entity_id(hass, entry_id, "sensor", control.key)
    if control.options:
        samples = [(value, slug) for value, slug in control.options]
    elif control.value_kind == "string":
        samples = [("sample", "sample")]
    else:
        middle = control.minimum + ((control.maximum - control.minimum) // 2)
        samples = [
            (value, str(value)) for value in (control.minimum, middle, control.maximum)
        ]
    for wire, expected in samples:
        fake.set_value(control.siid, control.piid, wire)
        await _refresh(hass, entry_id)
        assert hass.states.get(entity_id).state == expected


async def _show_binary_control(
    hass: HomeAssistant, entry_id: str, fake: FakeMiio, control: XiaomiControl
) -> None:
    entity_id = _entity_id(hass, entry_id, "binary_sensor", control.key)
    for wire, expected in ((0, "off"), (1, "on"), (False, "off"), (True, "on")):
        fake.set_value(control.siid, control.piid, wire)
        await _refresh(hass, entry_id)
        assert hass.states.get(entity_id).state == expected


def _assert_traffic_is_mapped(fake: FakeMiio, family: XiaomiModel) -> None:
    properties = {
        (item["siid"], item["piid"]) for item in family.property_overrides.values()
    }
    properties.update(
        (control.siid, control.piid)
        for control in family.controls
        if control.siid is not None and control.piid is not None
    )
    actions = {
        (item["siid"], item["aiid"]) for item in family.action_overrides.values()
    }
    actions.update(
        (control.siid, control.aiid)
        for control in family.controls
        if control.siid is not None and control.aiid is not None
    )
    outside_writes, outside_actions, unexpected = traffic_outside_map(
        fake.writes,
        fake.actions,
        fake.action_inputs,
        properties,
        actions,
    )
    assert not outside_writes
    assert not outside_actions
    assert not unexpected
