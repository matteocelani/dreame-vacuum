"""Spec coverage for xiaomi.vacuum.ov31gl, the Xiaomi Robot Vacuum 5."""

from __future__ import annotations

import json
from pathlib import Path

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
from custom_components.dreame_vacuum.xiaomi import (
    XiaomiControlException,
    invoke_control,
    read_control,
    resolve_family,
    write_control,
)
from custom_components.dreame_vacuum.xiaomi.controls import XiaomiControl
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_X20_MAX,
    XiaomiModel,
)
import pytest
from tests.xiaomi.helpers import FakeMiio, release_device, traffic_outside_map

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_SPECS = Path(__file__).parent / "specs"
_EVENT_REASON = (
    "needs council: completion events need a notification design; "
    "the integration polls and does not subscribe to MIoT events."
)
_SERVICE_REASONS = {
    1: "identity: manufacturer, model, and firmware come from miIO.info.",
    10: "map: map, room, and zone support stays off until its own change.",
}
_REASON_PREFIXES = ("identity:", "map:", "no ha meaning:", "needs council:")
_V2_ONLY_CONTROLS = {(20, 9), (20, 11)}
_PROPERTY_REASONS = {
    (2, 1): "no ha meaning: firmware is already exposed from miIO.info.",
    (2, 12): "map: zone ids.",
    (2, 13): "map: restricted areas.",
    (2, 14): "map: virtual walls.",
    (2, 15): "map: room ids are not readable.",
    (2, 16): "map: room information.",
    (2, 22): "map: carpet display is map rendering.",
    (2, 24): "no ha meaning: common params are neither readable nor writable.",
    (2, 27): "map: map-complete dialog.",
    (2, 39): "no ha meaning: button type is neither readable nor writable.",
    (2, 42): "needs council: user-defined sweep config needs a program editor.",
    (2, 43): "needs council: user-defined sweep id needs a program editor.",
    (2, 53): "needs council: water-check list is an opaque string.",
    (2, 56): "map: AI objects.",
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (2, 99): "map: sill geometry.",
    (2, 102): "map: automation furniture.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (17, 1): "no ha meaning: picture id is neither readable nor writable.",
    (17, 2): "needs council: unnamed picture string has no spec description.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "needs council: self-check values are internal component codes.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no spec description.",
    (20, 10): "needs council: unnamed writable field has no spec description.",
    (20, 12): "no ha meaning: unnamed field is neither readable nor writable.",
}
_ACTION_REASONS = {
    (2, 11): "map: room config takes a room-id parameter.",
    (2, 12): "map: set-zone takes a zone parameter.",
    (2, 13): "map: room clean config takes a room-id parameter.",
    (2, 14): "map: split room is a map edit.",
    (2, 15): "map: merge rooms is a map edit.",
    (2, 16): "map: room sweep takes a room-id parameter.",
    (2, 17): "map: build-map stays unmapped until map support.",
    (2, 23): "needs council: adding a schedule takes an order blob.",
    (2, 24): "needs council: modifying a schedule takes an order blob.",
    (2, 25): "needs council: deleting a schedule takes an order blob.",
    (2, 26): "needs council: remote direction requires a button-type parameter.",
    (2, 30): "no ha meaning: system info is a diagnostic fetch, not a user control.",
    (2, 33): "map: continue build-map stays unmapped until map support.",
    (2, 34): "map: stop build-map stays unmapped until map support.",
    (2, 35): "map: pause build-map stays unmapped until map support.",
    (2, 37): "map: zone sweep takes a zone parameter.",
    (2, 38): "needs council: adding a user sweep takes a config parameter.",
    (2, 39): "needs council: deleting a user sweep takes an id parameter.",
    (2, 40): "needs council: modifying a user sweep takes a config parameter.",
    (2, 42): "needs council: starting a user sweep takes an id parameter.",
    (2, 47): "map: the vacuum route takes a parameter and is map geometry.",
    (2, 48): "needs council: closing an abnormal card takes an opaque parameter.",
    (2, 52): "map: skip cleaning takes a room-id parameter.",
    (2, 53): "map: final cleaning takes a room-id parameter.",
    (2, 54): "map: temporary room cleaning takes a room-id parameter.",
    (2, 55): "map: temporary zone cleaning takes a zone parameter.",
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: AI recognize takes an object parameter.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (17, 1): "needs council: the picture request takes an id and returns an image.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
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

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_both_spec_versions_are_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason."""
    seen: set[tuple[str, int, int]] = set()
    counts: dict[str, tuple[int, int]] = {}
    for filename in ("ov31gl.json", "ov31gl_v1.json"):
        mapped_count = 0
        omitted_count = 0
        for kind, siid, iid, _spec in _items(filename):
            seen.add((kind, siid, iid))
            mapped = (
                (siid, iid) in _mapped_addresses(kind) if kind != "event" else False
            )
            reason = _reason(kind, siid, iid)
            assert mapped != bool(reason), (filename, kind, siid, iid, reason)
            if reason:
                assert reason.startswith(_REASON_PREFIXES), reason
                omitted_count += 1
            if mapped:
                name = _mapped_addresses(kind)[(siid, iid)]
                description = _spec_description(filename, kind, siid, iid)
                assert description or (siid, iid) in _V2_ONLY_CONTROLS
                assert name
                mapped_count += 1
        counts[filename] = (mapped_count, omitted_count)
    assert counts["ov31gl.json"] == (132, 103)
    assert counts["ov31gl_v1.json"] == (130, 100)
    for pair, reason in {**_PROPERTY_REASONS, **_ACTION_REASONS}.items():
        kind = "property" if pair in _PROPERTY_REASONS else "action"
        assert reason
        assert (kind, pair[0], pair[1]) in seen
    for siid in _SERVICE_REASONS:
        assert any(item[1] == siid for item in seen)


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


def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    socket_enabled: None,
) -> None:
    del socket_enabled
    family = _family()
    mapped_actions = _mapped_addresses("action")
    for filename in ("ov31gl.json", "ov31gl_v1.json"):
        for kind, siid, iid, spec in _items(filename):
            if kind == "action" and (siid, iid) in mapped_actions:
                assert not spec.get("in"), (filename, siid, iid)
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


def test_controls_match_the_spec() -> None:
    """Each control's options, range, and access follow the spec that defines it."""
    family = _family()
    current = _spec_index("ov31gl.json")
    previous = _spec_index("ov31gl_v1.json")
    keys = [control.key for control in family.controls]
    assert len(keys) == len(set(keys))
    for control in family.controls:
        if control.property_name:
            spec = current[("property", *_address(family, control.property_name))]
            _assert_options(control, spec)
            continue
        kind = "action" if control.aiid is not None else "property"
        pair = (
            control.siid,
            control.aiid if control.aiid is not None else control.piid,
        )
        assert (kind, pair[0], pair[1]) in current
        _assert_control_spec(control, current[(kind, pair[0], pair[1])])
        if pair in _V2_ONLY_CONTROLS:
            assert (kind, pair[0], pair[1]) not in previous
            continue
        _assert_control_spec(control, previous[(kind, pair[0], pair[1])])


def test_every_control_value_is_read_or_sent(socket_enabled: None) -> None:
    """Read every spec sample and send every writable value, including 0 through 255."""
    del socket_enabled
    family = _family()
    specs = _spec_index("ov31gl.json")
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            device._request_properties()
            for control in family.controls:
                if control.aiid is not None:
                    spec = specs[("action", control.siid, control.aiid)]
                    assert not spec.get("in")
                    invoke_control(device, control)
                    assert fake.actions[-1] == (control.siid, control.aiid)
                    assert fake.action_inputs[-1] == []
                    continue
                if control.property_name:
                    prop = DreameVacuumProperty[control.property_name]
                    mapping = family.property_overrides[control.property_name]
                    for value, _slug in control.options:
                        _force_set(device, prop, value)
                        assert fake.writes[-1] == (
                            mapping["siid"],
                            mapping["piid"],
                            value,
                        )
                    continue
                spec = specs[("property", control.siid, control.piid)]
                for sample in _property_samples(spec, every=True):
                    fake.set_value(control.siid, control.piid, sample)
                    family.refresh_controls(device)
                    assert read_control(device, control) == sample
                if not control.writable:
                    continue
                for sample in _property_samples(spec, every=True):
                    write_control(device, control, sample)
                    assert fake.writes[-1] == (control.siid, control.piid, sample)
                    assert read_control(device, control) == sample
        finally:
            release_device(device)
        _assert_traffic_is_mapped(fake)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    family = _family()
    alarm = next(item for item in family.controls if item.key == "xiaomi_alarm")
    button = next(item for item in family.controls if item.aiid is not None)
    with FakeMiio(MODEL_ROBOT_VACUUM_5) as fake:
        device = _connect()
        try:
            before = read_control(device, alarm)
            writes = len(fake.writes)
            actions = len(fake.actions)
            device._protocol.set_property = lambda *_args, **_kwargs: [{"code": -1}]
            with pytest.raises(XiaomiControlException):
                write_control(device, alarm, True)
            assert read_control(device, alarm) == before
            device._protocol.action = lambda *_args, **_kwargs: {"code": -1}
            with pytest.raises(XiaomiControlException):
                invoke_control(device, button)
            device._protocol.get_properties = lambda *_args, **_kwargs: None
            with pytest.raises(XiaomiControlException):
                family.refresh_controls(device)
            assert read_control(device, alarm) == before
            assert len(fake.writes) == writes
            assert len(fake.actions) == actions
        finally:
            release_device(device)


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


def _family() -> XiaomiModel:
    family = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert family is not None
    return family


def _mapped_addresses(kind: str) -> dict[tuple[int, int], str]:
    family = _family()
    found: dict[tuple[int, int], str] = {}
    if kind == "property":
        for name, item in family.property_overrides.items():
            found[(item["siid"], item["piid"])] = name
        for control in family.controls:
            if control.piid is None or control.siid is None:
                continue
            pair = (control.siid, control.piid)
            assert pair not in found
            found[pair] = control.key
        return found
    for name, item in family.action_overrides.items():
        found[(item["siid"], item["aiid"])] = name
    for control in family.controls:
        if control.aiid is None or control.siid is None:
            continue
        pair = (control.siid, control.aiid)
        assert pair not in found
        found[pair] = control.key
    return found


def _spec_index(filename: str) -> dict[tuple[str, int, int], dict[str, object]]:
    return {(kind, siid, iid): spec for kind, siid, iid, spec in _items(filename)}


def _address(family: XiaomiModel, name: str) -> tuple[int, int]:
    mapping = family.property_overrides[name]
    return mapping["siid"], mapping["piid"]


def _assert_control_spec(control: XiaomiControl, spec: dict[str, object]) -> None:
    if control.aiid is not None:
        assert not spec.get("in"), control.key
        return
    access = spec.get("access")
    assert isinstance(access, list)
    assert control.writable is ("write" in access)
    if control.options:
        _assert_options(control, spec)
        return
    if control.value_kind == "bool":
        assert spec.get("format") == "bool"
        return
    if control.value_kind == "string":
        assert spec.get("format") == "string"
        return
    bounds = spec.get("value-range")
    assert bounds == [control.minimum, control.maximum, control.step]


def _assert_options(control: XiaomiControl, spec: dict[str, object]) -> None:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    values = [item["value"] for item in listed if isinstance(item, dict)]
    assert [value for value, _slug in control.options] == values


def _property_samples(spec: dict[str, object], *, every: bool) -> list[object]:
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
        if every and (end - start) // step <= 255:
            return list(range(start, end + 1, step))
        middle = start + ((end - start) // 2)
        middle -= (middle - start) % step
        return list(dict.fromkeys((start, middle, end)))
    if spec.get("format") == "string":
        return ["", "sample"]
    return [0, 1]


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
    outside_writes, outside_actions, unexpected = traffic_outside_map(
        fake.writes,
        fake.actions,
        fake.action_inputs,
        set(_mapped_addresses("property")),
        set(_mapped_addresses("action")),
    )
    assert not outside_writes
    assert not outside_actions
    assert not unexpected


def _spec_description(filename: str, kind: str, siid: int, iid: int) -> str:
    for item_kind, item_siid, item_iid, spec in _items(filename):
        if item_kind == kind and item_siid == siid and item_iid == iid:
            description = spec.get("description") or ""
            assert isinstance(description, str)
            return description
    raise AssertionError((filename, kind, siid, iid))


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
