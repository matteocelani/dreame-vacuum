"""Spec coverage for xiaomi.vacuum.ov31gl, the Xiaomi Robot Vacuum 5.

Every MIoT property, action, and event is either mapped onto the Xiaomi base
or listed with the reason it stays off the wire. Mapped values are read and,
when the spec allows a write, sent. Home Assistant entities created for this
model are driven through the loopback device.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

from custom_components.dreame_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.exceptions import (
    InvalidActionException,
    UnavailableException,
)
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_X20_MAX,
)
import pytest
from tests.xiaomi.helpers import FakeMiio, release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_SPECS = Path(__file__).parent / "specs"
_FORBIDDEN = {(7, 2), (6, 3), (15, 1), (19, 1), (20, 1), (10, 7), (18, 1)}
_EVENT_REASON = (
    "The integration polls properties and does not subscribe to MIoT events."
)
_SERVICE_REASONS = {
    1: "Identity and firmware come from miIO.info, not service 1.",
    10: "Map, room, and zone support is a separate change and stays unmapped.",
    15: "Voice-pack download is not a Dreame voice property.",
    16: "IMU calibration is not a cleaning control.",
    17: "AI home images have no entity.",
    19: "Dust-bag life has no Dreame property that can stay off dock status.",
    20: "Unnamed plugin, self-check, and lidar fields stay off the shell.",
}
_PROPERTY_REASONS = {
    (2, 1): "Firmware is reported by miIO.info.",
    (2, 8): "Per-job repeat count is not the lifetime cleaning counter.",
    (2, 12): "Zone ids are map data and stay unmapped.",
    (2, 13): "Restricted areas are map data and stay unmapped.",
    (2, 14): "Virtual walls are map data and stay unmapped.",
    (2, 15): "Room ids are not readable and room cleaning stays unmapped.",
    (2, 16): "Room information is map data and stays unmapped.",
    (2, 17): "Last-clean time is not a separate sensor without map history.",
    (2, 18): "Base-station status is a string blob with no wash-base flag.",
    (2, 21): "Carpet avoidance is not the Dreame carpet-recognition encoding.",
    (2, 22): "Carpet display is map rendering and stays unmapped.",
    (2, 24): "Common params are not readable.",
    (2, 25): "Sleep status has no shell entity.",
    (2, 27): "Map-complete dialog is a map prompt and stays unmapped.",
    (2, 28): "Mop-wash enable would expose wash actions that are not mapped.",
    (2, 29): "Mop-wash frequency needs the wash base, which stays off.",
    (2, 30): "Wash-water output needs the wash base, which stays off.",
    (2, 31): "Drying time needs the wash base, which stays off.",
    (2, 34): "Auto mop dry needs the wash base, which stays off.",
    (2, 35): "Auto water change needs the wash base, which stays off.",
    (2, 36): "Use-detergent is not the Dreame auto-detergent encoding.",
    (2, 38): "Remote-dialog is not a cleaning control.",
    (2, 39): "Remote button type is not readable and remote control stays off.",
    (2, 41): "Hot-water wash needs the wash base, which stays off.",
    (2, 42): "User-defined sweep config is a map program and stays unmapped.",
    (2, 43): "User-defined sweep id is a map program and stays unmapped.",
    (2, 53): "Water-check list is a station string and stays unmapped.",
    (2, 54): "Water-check status needs a station flag that stays off.",
    (2, 56): "AI objects are map data and stay unmapped.",
    (2, 57): "Furniture is map data and stays unmapped.",
    (2, 58): "Carpet objects are map data and stay unmapped.",
    (2, 59): "Detergent self-delivery is not the Dreame auto-detergent encoding.",
    (2, 60): "Tankless water output uses a different enum than water volume.",
    (2, 61): "Tankless wash frequency needs the wash base, which stays off.",
    (2, 62): "Auto water-change install status needs the wash base.",
    (2, 65): "Vacuum route is not readable and is map geometry.",
    (2, 67): "Action result is a command echo, not a property the shell polls.",
    (2, 70): "Plugin reminders have no entity.",
    (2, 71): "Detergent reminder is not the mapped detergent-life sensor.",
    (2, 72): "Notice text has no entity.",
    (2, 74): "Sweep route values do not match the Dreame cleaning-route enum.",
    (2, 75): "Obstacle strategy is not the Dreame obstacle-avoidance bool.",
    (2, 76): "Carpet deep cleaning has no capability flag on this base.",
    (2, 77): "Carpet discriminate is not the Dreame carpet-recognition property.",
    (2, 78): "Sweep-carpet-first is left off so no new flag is derived.",
    (2, 79): "Mop swing has no capability flag on this base.",
    (2, 80): "Mop swing frequency values differ from other Xiaomi models.",
    (2, 81): "Wash-by-time needs the wash base, which stays off.",
    (2, 82): "Dust-arrest power levels do not match a Dreame property.",
    (2, 83): "Worry-free mode includes values with no Dreame cleaning mode.",
    (2, 84): "Wash-water temperature needs the wash base, which stays off.",
    (2, 88): "Drying progress needs the wash base, which stays off.",
    (2, 89): "Cleaning progress is read-only and the shell would write it.",
    (2, 90): "Dry time left needs the wash base, which stays off.",
    (2, 91): "Brush outswing has no capability flag on this base.",
    (2, 92): "Repeat mop wash needs the wash base, which stays off.",
    (2, 96): "Sweep-mop status duplicates the mapped status property.",
    (2, 97): "Sewage tank status needs dock status, which stays off.",
    (2, 98): "Station water-tank status is not the mapped mop-status bool.",
    (2, 99): "Sill geometry is map data and stays unmapped.",
    (2, 100): "Base-station tank status needs dock status, which stays off.",
    (2, 101): "Host tank status needs dock status, which stays off.",
    (2, 102): "Automation furniture is map data and stays unmapped.",
    (3, 3): "Battery voltage has no entity.",
    (4, 1): "Alarm is separate from the mapped volume control.",
    (5, 2): "Current lock is a read-only echo of the mapped child lock.",
    (11, 2): "Do-not-disturb time is one packed integer, not a start and end.",
    (11, 3): "Current do-not-disturb is a read-only echo of the mapped switch.",
    (18, 2): "Detergent delivery is not the Dreame auto-detergent encoding.",
    (18, 3): "Detergent delivery level is not a Dreame property.",
}
_ACTION_REASONS = {
    (2, 3): "Stop-and-dock duplicates the mapped stop and charge actions.",
    (2, 4): "Start-sweep duplicates start plus the cleaning-mode property.",
    (2, 5): "Start-mop duplicates start plus the cleaning-mode property.",
    (2, 6): "Start sweep-mop duplicates start plus the cleaning-mode property.",
    (2, 11): "Room config takes a room-id parameter and stays unmapped.",
    (2, 12): "Set-zone takes a zone parameter and stays unmapped.",
    (2, 13): "Room clean config takes a room-id parameter and stays unmapped.",
    (2, 14): "Split room is a map edit and stays unmapped.",
    (2, 15): "Merge rooms is a map edit and stays unmapped.",
    (2, 16): "Room sweep takes a room-id parameter and stays unmapped.",
    (2, 17): "Build-map is a map action and stays unmapped.",
    (2, 19): "Start mop wash needs the wash base, which stays off.",
    (2, 20): "Start dry needs the wash base, which stays off.",
    (2, 21): "Eject is not a Dreame cleaning action.",
    (2, 22): "Call-clean is not a Dreame cleaning action.",
    (2, 23): "Add schedule takes an order blob and stays unmapped.",
    (2, 24): "Modify schedule takes an order blob and stays unmapped.",
    (2, 25): "Delete schedule takes an order blob and stays unmapped.",
    (2, 26): "Remote control requires a button-type parameter.",
    (2, 27): "Try-listen is a voice preview and stays unmapped.",
    (2, 28): "Enter remote is not a Dreame cleaning action.",
    (2, 29): "Exit remote is not a Dreame cleaning action.",
    (2, 30): "System info is not a cleaning action.",
    (2, 31): "Stop mop wash needs the wash base, which stays off.",
    (2, 32): "Stop dry needs the wash base, which stays off.",
    (2, 33): "Continue build-map is a map action and stays unmapped.",
    (2, 34): "Stop build-map is a map action and stays unmapped.",
    (2, 35): "Pause build-map is a map action and stays unmapped.",
    (2, 36): "Back-to-wash needs the wash base, which stays off.",
    (2, 37): "Zone sweep takes a zone parameter and stays unmapped.",
    (2, 38): "Add user sweep takes a config parameter and stays unmapped.",
    (2, 39): "Delete user sweep takes an id parameter and stays unmapped.",
    (2, 40): "Modify user sweep takes a config parameter and stays unmapped.",
    (2, 42): "Start user sweep takes an id parameter and stays unmapped.",
    (2, 43): "Hair cut is not a Dreame cleaning action.",
    (2, 44): "Stop hair cut is not a Dreame cleaning action.",
    (2, 45): "Water self-check needs the wash base, which stays off.",
    (2, 46): "Cancel water self-check needs the wash base, which stays off.",
    (2, 47): "Vacuum route takes a parameter and is map geometry.",
    (2, 48): "Close abnormal card takes a parameter and stays unmapped.",
    (2, 49): "Base-station cleaning needs the wash base, which stays off.",
    (2, 50): "Sweep-before-mop duplicates start plus the cleaning-mode property.",
    (2, 51): "Stop working duplicates the mapped stop action.",
    (2, 52): "Skip cleaning takes a room-id parameter and stays unmapped.",
    (2, 53): "Final cleaning takes a room-id parameter and stays unmapped.",
    (2, 54): "Temporary room clean takes a room-id parameter and stays unmapped.",
    (2, 55): "Temporary zone clean takes a zone parameter and stays unmapped.",
    (2, 56): "Furniture cleaning takes a parameter and stays unmapped.",
    (2, 57): "Empty the station tank needs dock status, which stays off.",
    (2, 58): "Empty the host tank needs dock status, which stays off.",
    (2, 59): "Spot cleaning is not the mapped start action.",
    (2, 60): "AI recognize takes a parameter and stays unmapped.",
    (2, 62): "Common-object clean takes a parameter and stays unmapped.",
    (2, 63): "Station self-clean needs the wash base, which stays off.",
    (2, 64): "Stop station self-clean needs the wash base, which stays off.",
}
_STATE_AFTER_READ = {
    1: DreameVacuumState.IDLE,
    2: DreameVacuumState.CHARGING,
    3: DreameVacuumState.CHARGING,
    4: DreameVacuumState.SWEEPING,
    5: DreameVacuumState.PAUSED,
    6: DreameVacuumState.RETURNING,
    7: DreameVacuumState.RETURNING_TO_WASH,
    8: DreameVacuumState.REMOTE_CONTROL,
    9: DreameVacuumState.CHARGING_COMPLETED,
    10: DreameVacuumState.BUILDING,
    11: DreameVacuumState.UPGRADING,
    12: DreameVacuumState.STATION_CLEANING,
    13: DreameVacuumState.CHARGING,
    14: DreameVacuumState.STATION_CLEANING,
    15: DreameVacuumState.ERROR,
    16: DreameVacuumState.SWEEPING_AND_MOPPING,
    17: DreameVacuumState.MOPPING,
    18: DreameVacuumState.PAUSED,
    19: DreameVacuumState.RETURNING,
    20: DreameVacuumState.RETURNING_TO_WASH,
    21: DreameVacuumState.BUILDING,
    22: DreameVacuumState.WASHING,
    23: DreameVacuumState.CHARGING_COMPLETED,
    24: DreameVacuumState.RETURNING,
}
_ENTITIES = {
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
    ("sensor", "cleaning_count"),
    ("sensor", "cleaning_time"),
    ("sensor", "detergent_left"),
    ("sensor", "detergent_time_left"),
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

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def _document(filename: str) -> dict[str, object]:
    return json.loads((_SPECS / filename).read_text(encoding="utf-8"))


def _items(filename: str) -> list[tuple[str, int, int, dict[str, object]]]:
    found: list[tuple[str, int, int, dict[str, object]]] = []
    document = _document(filename)
    services = document["services"]
    assert isinstance(services, list)
    for service in services:
        assert isinstance(service, dict)
        siid = service["iid"]
        assert isinstance(siid, int)
        for kind, field in (
            ("property", "properties"),
            ("action", "actions"),
            ("event", "events"),
        ):
            raw = service.get(field) or []
            assert isinstance(raw, list)
            for item in raw:
                assert isinstance(item, dict)
                iid = item["iid"]
                assert isinstance(iid, int)
                found.append((kind, siid, iid, item))
    return found


def _reason(kind: str, siid: int, iid: int) -> str | None:
    if kind == "event":
        return _EVENT_REASON
    if siid in _SERVICE_REASONS:
        return _SERVICE_REASONS[siid]
    table = _PROPERTY_REASONS if kind == "property" else _ACTION_REASONS
    return table.get((siid, iid))


def _family():
    family = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert family is not None
    return family


def _mapped_addresses(kind: str) -> dict[tuple[int, int], str]:
    family = _family()
    if kind == "property":
        return {
            (item["siid"], item["piid"]): name
            for name, item in family.property_overrides.items()
        }
    return {
        (item["siid"], item["aiid"]): name
        for name, item in family.action_overrides.items()
    }


def _samples(spec: dict[str, object]) -> list[object]:
    if spec.get("format") == "bool":
        return [False, True]
    listed = spec.get("value-list")
    if isinstance(listed, list):
        return [item["value"] for item in listed if isinstance(item, dict)]
    bounds = spec.get("value-range")
    if isinstance(bounds, list) and len(bounds) == 3:
        start, end, step = bounds
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert isinstance(step, int)
        middle = start + ((end - start) // 2)
        middle -= (middle - start) % step
        return list(dict.fromkeys((start, middle, end)))
    if spec.get("format") == "string":
        return ["", "sample"]
    return [0, 1]


def _write_samples(spec: dict[str, object]) -> list[object]:
    bounds = spec.get("value-range")
    if isinstance(bounds, list) and len(bounds) == 3:
        start, end, step = bounds
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert isinstance(step, int)
        if (end - start) // step <= 100:
            return list(range(start, end + 1, step))
    return _samples(spec)


def _connect() -> DreameVacuumDevice:
    device = DreameVacuumDevice(
        "Vacuum 5",
        "127.0.0.1",
        _TOKEN,
        _MAC,
        account_type="mi",
        family_resolver=resolve_family,
    )
    device.connect_device()
    return device


def _assert_traffic_is_mapped(fake: FakeMiio) -> None:
    properties = set(_mapped_addresses("property"))
    actions = set(_mapped_addresses("action"))
    write_pairs = {(siid, piid) for siid, piid, _value in fake.writes}
    assert write_pairs <= properties
    assert set(fake.actions) <= actions
    # Dreame default addresses stay silent unless this model's spec maps them.
    assert not (set(fake.actions) - actions) & _FORBIDDEN
    assert not (write_pairs - properties) & _FORBIDDEN
    for payload in fake.action_inputs:
        assert payload in ([], None)


def test_both_spec_versions_are_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason."""
    seen: set[tuple[str, int, int]] = set()
    for filename in ("ov31gl.json", "ov31gl_v1.json"):
        for kind, siid, iid, _spec in _items(filename):
            seen.add((kind, siid, iid))
            mapped = (
                (siid, iid) in _mapped_addresses(kind) if kind != "event" else False
            )
            reason = _reason(kind, siid, iid)
            assert mapped != bool(reason), (filename, kind, siid, iid, reason)
            if mapped:
                name = _mapped_addresses(kind)[(siid, iid)]
                assert _spec_description(filename, kind, siid, iid)
                assert name
    for pair, reason in {**_PROPERTY_REASONS, **_ACTION_REASONS}.items():
        kind = "property" if pair in _PROPERTY_REASONS else "action"
        assert reason
        assert (kind, pair[0], pair[1]) in seen
    for siid in _SERVICE_REASONS:
        assert any(item[1] == siid for item in seen)


def _spec_description(filename: str, kind: str, siid: int, iid: int) -> str:
    for item_kind, item_siid, item_iid, spec in _items(filename):
        if item_kind == kind and item_siid == siid and item_iid == iid:
            description = spec.get("description") or ""
            assert isinstance(description, str)
            return description
    raise AssertionError((filename, kind, siid, iid))


def test_every_mapped_property_reads_each_spec_value(
    socket_enabled: None,
) -> None:
    del socket_enabled
    family = _family()
    x20 = resolve_family(MODEL_X20_MAX)
    assert x20 is not None
    assert x20.convert_incoming("STATE", 8) == DreameVacuumState.REMOTE_CONTROL
    assert family.convert_incoming("STATE", 8) == 19
    specs = {
        (siid, iid): spec
        for kind, siid, iid, spec in _items("ov31gl.json")
        if kind == "property"
    }
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            assert device.info is not None
            assert device.info.model == MODEL_ROBOT_VACUUM_5
            assert fake.actions == []
            assert fake.writes == []
            for name, mapping in family.property_overrides.items():
                prop = DreameVacuumProperty[name]
                address = (mapping["siid"], mapping["piid"])
                for sample in _samples(specs[address]):
                    if prop is DreameVacuumProperty.CLEANING_PROPERTIES:
                        # The shell never polls this string. A pushed value still converts.
                        device._handle_properties(
                            [
                                {
                                    "did": str(prop.value),
                                    "siid": address[0],
                                    "piid": address[1],
                                    "code": 0,
                                    "value": sample,
                                }
                            ]
                        )
                    else:
                        fake.set_value(address[0], address[1], sample)
                        device._request_properties([prop])
                    assert device.get_property(prop) == family.convert_incoming(
                        name, sample
                    )
            requested: list[tuple[int, int]] = []

            def record(
                parameters: list[dict[str, int]],
                retry_count: int = 1,
                timeout: object = None,
            ) -> list[dict[str, object]]:
                del retry_count, timeout
                requested.extend((item["siid"], item["piid"]) for item in parameters)
                return [
                    {
                        "did": item["did"],
                        "siid": item["siid"],
                        "piid": item["piid"],
                        "code": 0,
                        "value": 0,
                    }
                    for item in parameters
                ]

            device._protocol.get_properties = record
            device._request_properties()
            cleaning = family.property_overrides["CLEANING_PROPERTIES"]
            assert (cleaning["siid"], cleaning["piid"]) not in requested
            assert device.capability.new_state is False
        finally:
            release_device(device)
        _assert_traffic_is_mapped(fake)


def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    socket_enabled: None,
) -> None:
    del socket_enabled
    family = _family()
    specs = {
        (siid, iid): spec
        for kind, siid, iid, spec in _items("ov31gl.json")
        if kind == "property"
    }
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            for name, mapping in family.property_overrides.items():
                spec = specs[(mapping["siid"], mapping["piid"])]
                access = spec.get("access")
                assert isinstance(access, list)
                if "write" not in access:
                    continue
                prop = DreameVacuumProperty[name]
                if spec.get("format") == "bool":
                    _send_bool(device, fake, prop, mapping)
                    continue
                for sample in _write_samples(spec):
                    stored = family.convert_incoming(name, sample)
                    _force_set(device, prop, stored)
                    assert fake.writes[-1][0] == mapping["siid"]
                    assert fake.writes[-1][1] == mapping["piid"]
                    assert fake.writes[-1][2] == family.convert_outgoing(name, stored)
            sent_volume = {
                value
                for siid, piid, value in fake.writes
                if (siid, piid)
                == (
                    family.property_overrides["VOLUME"]["siid"],
                    family.property_overrides["VOLUME"]["piid"],
                )
            }
            assert sent_volume == set(range(101))
            before = len(fake.writes)
            assert (
                device.set_property(DreameVacuumProperty.MAP_DATA, "blocked") is False
            )
            assert len(fake.writes) == before
        finally:
            release_device(device)
        _assert_traffic_is_mapped(fake)


def _send_bool(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    prop: DreameVacuumProperty,
    mapping: dict[str, int],
) -> None:
    for value in (1, 0, True, False):
        _force_set(device, prop, value)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], value)


def _force_set(
    device: DreameVacuumDevice, prop: DreameVacuumProperty, value: object
) -> None:
    current = device.get_property(prop)
    if current == value:
        other: object = 0 if value != 0 else 1
        if prop is DreameVacuumProperty.VOLUME:
            other = 1 if value == 0 else 0
        assert device.set_property(prop, other) is True
    assert device.set_property(prop, value) is True


def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    socket_enabled: None,
) -> None:
    del socket_enabled
    family = _family()
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            for name in family.action_overrides:
                action = DreameVacuumAction[name]
                before = len(fake.actions)
                if name == "START_AUTO_EMPTY":
                    with pytest.raises(UnavailableException):
                        device.call_action(action)
                    assert len(fake.actions) == before
                    continue
                result = device.call_action(action)
                assert result is not None
                assert result.get("code") == 0
                assert len(fake.actions) == before + 1
                assert fake.action_inputs[-1] == []
            for action in (
                DreameVacuumAction.PLAY_SOUND,
                DreameVacuumAction.REQUEST_MAP,
                DreameVacuumAction.BACKUP_MAP,
                DreameVacuumAction.UPDATE_MAP_DATA,
                DreameVacuumAction.RESET_SILVER_ION,
                DreameVacuumAction.START_WASHING,
            ):
                before = len(fake.actions)
                with pytest.raises(InvalidActionException):
                    device.call_action(action, {"in": [1]})
                assert len(fake.actions) == before
        finally:
            release_device(device)
        _assert_traffic_is_mapped(fake)
        assert set(fake.actions) == {
            (item["siid"], item["aiid"]) for item in family.action_overrides.values()
        } - {
            (
                family.action_overrides["START_AUTO_EMPTY"]["siid"],
                family.action_overrides["START_AUTO_EMPTY"]["aiid"],
            )
        }


def test_every_status_wire_reaches_the_shell_state(socket_enabled: None) -> None:
    del socket_enabled
    family = _family()
    state = family.property_overrides["STATE"]
    charging = family.property_overrides["CHARGING_STATUS"]
    error = family.property_overrides["ERROR"]
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            for wire, expected in _STATE_AFTER_READ.items():
                fake.set_value(charging["siid"], charging["piid"], 2)
                fake.set_value(error["siid"], error["piid"], 0)
                fake.set_value(state["siid"], state["piid"], wire)
                device._request_properties(
                    [
                        DreameVacuumProperty.STATE,
                        DreameVacuumProperty.CHARGING_STATUS,
                        DreameVacuumProperty.ERROR,
                    ]
                )
                assert device.status.state is expected, wire
            fake.set_value(charging["siid"], charging["piid"], 1)
            fake.set_value(state["siid"], state["piid"], 2)
            device._request_properties(
                [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
            )
            assert device.status.docked is True
            assert device.status.state is DreameVacuumState.CHARGING
            fake.set_value(charging["siid"], charging["piid"], 2)
            fake.set_value(state["siid"], state["piid"], 1)
            device._request_properties(
                [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
            )
            assert device.status.state is DreameVacuumState.IDLE
            device.start()
            device._request_properties([DreameVacuumProperty.STATE])
            assert device.status.state is DreameVacuumState.SWEEPING
            device.pause()
            device._request_properties([DreameVacuumProperty.STATE])
            assert device.status.state is DreameVacuumState.PAUSED
            device.start()
            device._request_properties([DreameVacuumProperty.STATE])
            assert device.status.state is DreameVacuumState.SWEEPING
            assert fake.actions[-1] == (
                family.action_overrides["RESUME"]["siid"],
                family.action_overrides["RESUME"]["aiid"],
            )
            device.return_to_base()
            device._request_properties(
                [DreameVacuumProperty.STATE, DreameVacuumProperty.CHARGING_STATUS]
            )
            assert device.status.state is DreameVacuumState.CHARGING
            fake.set_value(error["siid"], error["piid"], 1)
            fake.set_value(charging["siid"], charging["piid"], 2)
            fake.set_value(state["siid"], state["piid"], 1)
            device._request_properties(
                [
                    DreameVacuumProperty.ERROR,
                    DreameVacuumProperty.STATE,
                    DreameVacuumProperty.CHARGING_STATUS,
                ]
            )
            assert device.status.state is DreameVacuumState.ERROR
        finally:
            release_device(device)
        _assert_traffic_is_mapped(fake)


@pytest.mark.ha
async def test_home_assistant_entities_cover_every_exposed_control(
    hass,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Drive every entity this model creates and keep traffic on the map."""
    del socket_enabled, integration_package
    from custom_components.dreame_vacuum.dreame import VERSION

    family = _family()
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        entry = _entry(hass, VERSION)
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        device = hass.data[DOMAIN][entry.entry_id].device
        try:
            keys = _registry_keys(hass, entry.entry_id)
            assert keys == _ENTITIES
            assert not any(domain == "time" for domain, _key in keys)
            await _exercise_selects_switches_number_and_buttons(hass, fake, family)
            await _exercise_vacuum_states(hass, entry.entry_id, fake, family)
            await _exercise_sensors(hass, entry.entry_id, fake, family)
            assert hass.states.get(
                _entity_id(hass, entry.entry_id, "sensor", "firmware_version")
            )
        finally:
            assert await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            release_device(device)
    _assert_traffic_is_mapped(fake)


def _entry(hass, version: int):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN

    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="Vacuum 5 Sim",
        data={
            CONF_NAME: "Vacuum 5 Sim",
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


def _registry_keys(hass, entry_id: str) -> set[tuple[str, str]]:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    keys: set[tuple[str, str]] = set()
    prefix = f"{_MAC}_"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        assert item.unique_id.startswith(prefix)
        keys.add((item.domain, item.unique_id.removeprefix(prefix)))
    return keys


def _entity_id(hass, entry_id: str, domain: str, key: str) -> str:
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)
    unique_id = f"{_MAC}_{key}"
    for item in er.async_entries_for_config_entry(registry, entry_id):
        if item.domain == domain and item.unique_id == unique_id:
            return item.entity_id
    raise AssertionError((domain, key))


async def _refresh(hass, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()


async def _exercise_selects_switches_number_and_buttons(hass, fake, family) -> None:
    entry_id = _config_entry_id(hass)
    await _select_each(hass, entry_id, "suction_level")
    await _select_each(hass, entry_id, "cleaning_mode")
    charging = family.property_overrides["WATER_TANK"]
    fake.set_value(charging["siid"], charging["piid"], True)
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
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": _entity_id(hass, entry_id, "number", "volume"), "value": 0},
        blocking=True,
    )
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": _entity_id(hass, entry_id, "number", "volume"), "value": 50},
        blocking=True,
    )
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": _entity_id(hass, entry_id, "number", "volume"), "value": 100},
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
    from homeassistant.exceptions import HomeAssistantError

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


async def _select_each(hass, entry_id: str, key: str) -> None:
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


def _config_entry_id(hass) -> str:
    entry_ids = list(hass.data[DOMAIN])
    assert len(entry_ids) == 1
    return entry_ids[0]


async def _exercise_vacuum_states(hass, entry_id: str, fake, family) -> None:
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


async def _exercise_sensors(hass, entry_id: str, fake, family) -> None:
    samples = {
        "BATTERY_LEVEL": (55, "55"),
        "CLEANED_AREA": (12, "12"),
        "CLEANING_TIME": (9, "9"),
        "CLEANING_COUNT": (4, "4"),
        "TOTAL_CLEANED_AREA": (30, "30"),
        "TOTAL_CLEANING_TIME": (15, "15"),
        "DETERGENT_LEFT": (40, "40"),
        "DETERGENT_TIME_LEFT": (6, "6"),
        "MAIN_BRUSH_LEFT": (80, "80"),
        "ERROR": (0, "no_error"),
    }
    for name, (wire, _expected) in samples.items():
        mapping = family.property_overrides[name]
        fake.set_value(mapping["siid"], mapping["piid"], wire)
    await _refresh(hass, entry_id)
    for name, (_wire, expected) in samples.items():
        entity_id = _entity_id(hass, entry_id, "sensor", name.lower())
        state = hass.states.get(entity_id)
        assert state is not None
        assert expected in state.state
