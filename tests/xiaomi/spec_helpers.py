"""Shared MIoT spec readers and wire exercises for Xiaomi model tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

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

LOOPBACK_HOST: Final = "127.0.0.1"
LOOPBACK_TOKEN: Final = "00" * 16
LOOPBACK_MAC: Final = "00:00:00:00:00:00"
_SPECS: Final = Path(__file__).parent / "specs"
_STRINGS: Final = Path("custom_components/dreame_vacuum/strings.json")
_WRITE_SAMPLE_LIMIT: Final = 100
_CONTROL_SAMPLE_LIMIT: Final = 255
_EVENT_REASON: Final = (
    "needs council: completion events need a notification design; "
    "the integration polls and does not subscribe to MIoT events."
)
_SERVICE_REASONS: Final[dict[int, str]] = {
    1: "identity: manufacturer, model, and firmware come from miIO.info.",
    10: "map: map, room, and zone support stays off until its own change.",
}
_REASON_PREFIXES: Final = ("identity:", "map:", "no ha meaning:", "needs council:")
_REFUSED_ACTIONS: Final = (
    DreameVacuumAction.PLAY_SOUND,
    DreameVacuumAction.REQUEST_MAP,
    DreameVacuumAction.BACKUP_MAP,
    DreameVacuumAction.UPDATE_MAP_DATA,
    DreameVacuumAction.RESET_SILVER_ION,
    DreameVacuumAction.START_WASHING,
)


@dataclass(frozen=True, slots=True)
class SpecCase:
    """Model id, spec file, and omission tables for one Xiaomi spec suite."""

    model: str
    device_name: str
    spec_filename: str
    property_reasons: Mapping[tuple[int, int], str]
    action_reasons: Mapping[tuple[int, int], str]
    state_after_read: Mapping[int, DreameVacuumState]
    classification_counts: Mapping[str, tuple[int, int]]
    spec_type: str | None = None
    reason_prefix_counts: Mapping[str, int] | None = None
    absent_items: tuple[tuple[str, int, int], ...] = ()
    checked_events: tuple[tuple[int, int], ...] = ()
    version_only_controls: frozenset[tuple[int, int]] = frozenset()
    action_spec_filenames: tuple[str, ...] = ()
    previous_spec_filename: str | None = None


# S60+ and S60 omit the same items. Each model maps only its own extra addresses.
S60_CLASS_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (2, 99): "map: sill geometry.",
    (2, 102): "map: automation furniture.",
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (2, 106): "no ha meaning: sweep params are neither readable nor writable.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}
S60_CLASS_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
    (2, 10): "map: zone config takes a zone-id parameter.",
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
    (2, 41): "needs council: setting a user sweep takes a config parameter.",
    (2, 42): "needs council: starting a user sweep takes an id parameter.",
    (2, 47): "map: the vacuum route takes a parameter and is map geometry.",
    (2, 48): "needs council: closing an abnormal card takes an opaque parameter.",
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: operating an AI object takes an opaque parameter.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 16): "needs council: OTA info takes a parameter and must not start an update.",
}
S60_CLASS_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
    25: DreameVacuumState.UNKNOWN,
    26: DreameVacuumState.CLEAN_SUMMON,
    27: DreameVacuumState.SWEEPING,
}


def load_spec_document(filename: str) -> dict[str, object]:
    """Load one published MIoT spec document."""
    loaded = json.loads((_SPECS / filename).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def spec_items(filename: str) -> list[tuple[str, int, int, dict[str, object]]]:
    """Return every property, action, and event as kind, siid, iid, and spec."""
    found: list[tuple[str, int, int, dict[str, object]]] = []
    document = load_spec_document(filename)
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


def spec_index(filename: str) -> dict[tuple[str, int, int], dict[str, object]]:
    """Index one spec by kind, siid, and iid."""
    return {(kind, siid, iid): spec for kind, siid, iid, spec in spec_items(filename)}


def normalize_spec(value: object, model_codes: tuple[str, ...]) -> object:
    """Replace model codes in spec text so two documents can be compared."""
    if isinstance(value, str):
        normalized = value
        for code in model_codes:
            normalized = normalized.replace(code, "model")
        return normalized
    if isinstance(value, dict):
        return {key: normalize_spec(item, model_codes) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_spec(item, model_codes) for item in value]
    return value


def spec_samples(
    spec: Mapping[str, object],
    *,
    full_range_limit: int | None = None,
) -> list[object]:
    """Return wire samples for one property spec.

    When full_range_limit is set and the inclusive range spans at most that
    many steps, every value is returned. Otherwise the samples are the ends
    and the midpoint.
    """
    if spec.get("format") == "bool":
        return [False, True]
    listed = spec.get("value-list")
    if isinstance(listed, list):
        return [item["value"] for item in listed if isinstance(item, dict)]
    bounds = _range_bounds(spec)
    if bounds is not None:
        start, end, step = bounds
        if full_range_limit is not None and (end - start) // step <= full_range_limit:
            return list(range(start, end + 1, step))
        middle = start + ((end - start) // 2)
        middle -= (middle - start) % step
        return list(dict.fromkeys((start, middle, end)))
    if spec.get("format") == "string":
        return ["", "sample"]
    return [0, 1]


def omission_reason(
    kind: str,
    siid: int,
    iid: int,
    *,
    property_reasons: Mapping[tuple[int, int], str],
    action_reasons: Mapping[tuple[int, int], str],
) -> str | None:
    """Return the omission reason for one spec item, or None when it is mapped."""
    if kind == "event":
        return _EVENT_REASON
    if siid in _SERVICE_REASONS:
        return _SERVICE_REASONS[siid]
    table = property_reasons if kind == "property" else action_reasons
    return table.get((siid, iid))


def mapped_addresses(family: XiaomiModel, kind: str) -> dict[tuple[int, int], str]:
    """Return mapped addresses and the property, action, or control that owns each."""
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


def property_address(family: XiaomiModel, name: str) -> tuple[int, int]:
    """Return the siid and piid of one mapped property."""
    mapping = family.property_overrides[name]
    return mapping["siid"], mapping["piid"]


def spec_description(filename: str, kind: str, siid: int, iid: int) -> str:
    """Return the description of one spec item."""
    for item_kind, item_siid, item_iid, spec in spec_items(filename):
        if item_kind == kind and item_siid == siid and item_iid == iid:
            description = spec.get("description") or ""
            assert isinstance(description, str)
            return description
    raise AssertionError((filename, kind, siid, iid))


def assert_control_options(control: XiaomiControl, spec: Mapping[str, object]) -> None:
    """Assert a control's option values follow the spec value list, in order."""
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    values = [item["value"] for item in listed if isinstance(item, dict)]
    assert [value for value, _slug in control.options] == values


def assert_control_matches_spec(
    control: XiaomiControl, spec: Mapping[str, object]
) -> None:
    """Assert one control's access, options, and range follow its spec item."""
    if control.aiid is not None:
        assert not spec.get("in"), control.key
        return
    access = spec.get("access")
    assert isinstance(access, list)
    assert control.writable is ("write" in access)
    if control.options:
        assert_control_options(control, spec)
        return
    if control.value_kind == "bool":
        assert spec.get("format") == "bool"
        return
    if control.value_kind == "string":
        assert spec.get("format") == "string"
        return
    bounds = spec.get("value-range")
    assert bounds == [control.minimum, control.maximum, control.step]


def require_family(model: str) -> XiaomiModel:
    """Return the installed family for a model id."""
    family = resolve_family(model)
    assert family is not None
    return family


def connect_device(name: str) -> DreameVacuumDevice:
    """Connect one loopback device and return it after the handshake."""
    device = DreameVacuumDevice(
        name,
        LOOPBACK_HOST,
        LOOPBACK_TOKEN,
        LOOPBACK_MAC,
        account_type="mi",
        family_resolver=resolve_family,
    )
    device.connect_device()
    return device


def assert_traffic_is_mapped(fake: FakeMiio, family: XiaomiModel) -> None:
    """Assert every write and action stayed on a mapped address."""
    outside_writes, outside_actions, unexpected = traffic_outside_map(
        fake.writes,
        fake.actions,
        fake.action_inputs,
        set(mapped_addresses(family, "property")),
        set(mapped_addresses(family, "action")),
    )
    assert not outside_writes
    assert not outside_actions
    assert not unexpected


def force_property_set(
    device: DreameVacuumDevice, prop: DreameVacuumProperty, value: object
) -> None:
    """Set a property even when the device already stores that value."""
    current = device.get_property(prop)
    if current == value:
        other: object = 0 if value != 0 else 1
        if prop is DreameVacuumProperty.VOLUME:
            other = 1 if value == 0 else 0
        assert device.set_property(prop, other) is True
    assert device.set_property(prop, value) is True


def send_bool_values(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    prop: DreameVacuumProperty,
    mapping: Mapping[str, int],
) -> None:
    """Write both integer and boolean forms and assert each wire value."""
    for value in (1, 0, True, False):
        force_property_set(device, prop, value)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], value)


def assert_spec_is_fully_classified(case: SpecCase) -> None:
    """Assert every spec item is mapped or omitted with one allowed reason."""
    if case.spec_type is not None:
        document = load_spec_document(case.spec_filename)
        assert document["type"] == case.spec_type
    family = require_family(case.model)
    seen: set[tuple[str, int, int]] = set()
    for filename, expected in case.classification_counts.items():
        assert _classify_file(case, family, filename, seen) == expected
    if case.reason_prefix_counts is not None:
        assert _reason_prefix_counts(case) == dict(case.reason_prefix_counts)
    for kind, siid, iid in case.absent_items:
        assert (kind, siid, iid) not in seen
    for siid, iid in case.checked_events:
        assert (
            omission_reason(
                "event",
                siid,
                iid,
                property_reasons=case.property_reasons,
                action_reasons=case.action_reasons,
            )
            == _EVENT_REASON
        )
    for pair, reason in {**case.property_reasons, **case.action_reasons}.items():
        kind = "property" if pair in case.property_reasons else "action"
        assert reason
        assert (kind, pair[0], pair[1]) in seen
    for siid in _SERVICE_REASONS:
        assert any(item[1] == siid for item in seen)


def assert_controls_have_english_names(case: SpecCase) -> None:
    """Assert each control key and option slug has an English translation."""
    strings = json.loads(_STRINGS.read_text(encoding="utf-8"))
    entities = strings["entity"]
    assert isinstance(entities, dict)
    for control in require_family(case.model).controls:
        domain = entities[str(control.domain)]
        assert isinstance(domain, dict)
        block = domain[control.key]
        assert isinstance(block, dict)
        assert block["name"]
        if not control.options:
            continue
        states = block["state"]
        assert isinstance(states, dict)
        for _value, slug in control.options:
            assert slug in states


def exercise_mapped_property_reads(case: SpecCase) -> None:
    """Read every mapped property sample and keep cleaning strings off the poll."""
    family = require_family(case.model)
    _assert_remote_state_codec(family)
    specs = _property_specs(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _assert_device_is_quiet(device, fake, case.model)
            _read_each_mapped_property(device, fake, family, specs)
            _assert_cleaning_properties_are_not_polled(device, family)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_writable_values(case: SpecCase) -> None:
    """Send every writable sample and refuse a property this model does not map."""
    family = require_family(case.model)
    specs = _property_specs(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _send_each_writable_value(device, fake, family, specs)
            _assert_volume_span_and_blocked_map(device, fake, family)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_mapped_actions(case: SpecCase) -> None:
    """Invoke every mapped action and refuse actions that need parameters."""
    family = require_family(case.model)
    _assert_mapped_actions_take_no_input(case, family)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _invoke_each_mapped_action(device, fake, family)
            _refuse_parameterized_actions(device, fake)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)
        expected = {
            (item["siid"], item["aiid"]) for item in family.action_overrides.values()
        }
        auto_empty = family.action_overrides.get("START_AUTO_EMPTY")
        if auto_empty is not None:
            expected.discard((auto_empty["siid"], auto_empty["aiid"]))
        assert set(fake.actions) == expected


def exercise_status_wires(case: SpecCase) -> None:
    """Drive every published status wire through the shell state machine."""
    family = require_family(case.model)
    state = family.property_overrides["STATE"]
    charging = family.property_overrides["CHARGING_STATUS"]
    error = family.property_overrides["ERROR"]
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            _assert_each_status_wire(device, fake, case, state, charging, error)
            _assert_shell_transitions(device, fake, family, state, charging, error)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def assert_controls_match_spec(case: SpecCase) -> None:
    """Assert each control's options, range, and access follow its spec item."""
    family = require_family(case.model)
    current = spec_index(case.spec_filename)
    previous = (
        None
        if case.previous_spec_filename is None
        else spec_index(case.previous_spec_filename)
    )
    keys = [control.key for control in family.controls]
    assert len(keys) == len(set(keys))
    for control in family.controls:
        _assert_one_control(case, family, control, current, previous)


def exercise_control_values(case: SpecCase) -> None:
    """Read every control sample and send every writable value, including 0-255."""
    family = require_family(case.model)
    specs = spec_index(case.spec_filename)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            device._request_properties()
            for control in family.controls:
                _exercise_one_control(device, fake, family, specs, control)
        finally:
            release_device(device)
        assert_traffic_is_mapped(fake, family)


def exercise_rejected_control_traffic(case: SpecCase) -> None:
    """Assert a refused read or write leaves the stored value unchanged."""
    family = require_family(case.model)
    alarm = next(item for item in family.controls if item.key == "xiaomi_alarm")
    button = next(item for item in family.controls if item.aiid is not None)
    with FakeMiio(case.model) as fake:
        device = connect_device(case.device_name)
        try:
            before = read_control(device, alarm)
            writes = len(fake.writes)
            actions = len(fake.actions)
            device._protocol.set_property = _refuse_write
            with pytest.raises(XiaomiControlException):
                write_control(device, alarm, True)
            assert read_control(device, alarm) == before
            device._protocol.action = _refuse_action
            with pytest.raises(XiaomiControlException):
                invoke_control(device, button)
            device._protocol.get_properties = _refuse_read
            with pytest.raises(XiaomiControlException):
                family.refresh_controls(device)
            assert read_control(device, alarm) == before
            assert len(fake.writes) == writes
            assert len(fake.actions) == actions
        finally:
            release_device(device)


def _property_specs(filename: str) -> dict[tuple[int, int], dict[str, object]]:
    """Index property items by siid and piid."""
    return {
        (siid, iid): spec
        for kind, siid, iid, spec in spec_items(filename)
        if kind == "property"
    }


def _classify_file(
    case: SpecCase,
    family: XiaomiModel,
    filename: str,
    seen: set[tuple[str, int, int]],
) -> tuple[int, int]:
    """Classify one spec file and return its mapped and omitted counts."""
    mapped_count = 0
    omitted_count = 0
    for kind, siid, iid, _spec in spec_items(filename):
        seen.add((kind, siid, iid))
        mapped = (
            (siid, iid) in mapped_addresses(family, kind) if kind != "event" else False
        )
        reason = omission_reason(
            kind,
            siid,
            iid,
            property_reasons=case.property_reasons,
            action_reasons=case.action_reasons,
        )
        assert mapped != bool(reason), (filename, kind, siid, iid, reason)
        if reason:
            assert reason.startswith(_REASON_PREFIXES), reason
            omitted_count += 1
        if mapped:
            name = mapped_addresses(family, kind)[(siid, iid)]
            published = _has_published_name(_spec)
            version_only = (siid, iid) in case.version_only_controls
            assert published or version_only
            assert name
            mapped_count += 1
    return mapped_count, omitted_count


def _has_published_name(spec: Mapping[str, object]) -> bool:
    """Return whether the item, or every value it lists, has a description."""
    if spec.get("description"):
        return True
    # Custom services name each value and leave the property description empty.
    listed = spec.get("value-list")
    if not isinstance(listed, list) or not listed:
        return False
    return all(isinstance(item, dict) and item.get("description") for item in listed)


def _reason_prefix_counts(case: SpecCase) -> dict[str, int]:
    """Count omission-reason prefixes across the case's spec files."""
    prefixes: dict[str, int] = {}
    for filename in case.classification_counts:
        for kind, siid, iid, _spec in spec_items(filename):
            reason = omission_reason(
                kind,
                siid,
                iid,
                property_reasons=case.property_reasons,
                action_reasons=case.action_reasons,
            )
            if not reason:
                continue
            prefix = reason.split(":", 1)[0]
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
    return prefixes


def _assert_remote_state_codec(family: XiaomiModel) -> None:
    """Assert wire 8 is remote control on X20 Max and a raw code on this base."""
    x20 = resolve_family(MODEL_X20_MAX)
    vacuum_5 = resolve_family(MODEL_ROBOT_VACUUM_5)
    assert x20 is not None
    assert vacuum_5 is not None
    assert x20.convert_incoming("STATE", 8) == DreameVacuumState.REMOTE_CONTROL
    assert vacuum_5.convert_incoming("STATE", 8) == 19
    assert family.convert_incoming("STATE", 8) == 19


def _assert_device_is_quiet(
    device: DreameVacuumDevice, fake: FakeMiio, model: str
) -> None:
    """Assert the handshake identified the model and sent no commands."""
    assert device.info is not None
    assert device.info.model == model
    assert fake.actions == []
    assert fake.writes == []


def _read_each_mapped_property(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[int, int], Mapping[str, object]],
) -> None:
    """Read or push every sample and assert the converted property value."""
    for name, mapping in family.property_overrides.items():
        prop = DreameVacuumProperty[name]
        address = (mapping["siid"], mapping["piid"])
        for sample in spec_samples(specs[address]):
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
            assert device.get_property(prop) == family.convert_incoming(name, sample)


def _assert_cleaning_properties_are_not_polled(
    device: DreameVacuumDevice, family: XiaomiModel
) -> None:
    """Assert a full poll skips the cleaning-properties string."""
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


def _send_each_writable_value(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[int, int], Mapping[str, object]],
) -> None:
    """Send every writable sample, expanding ranges of at most 100 steps."""
    for name, mapping in family.property_overrides.items():
        spec = specs[(mapping["siid"], mapping["piid"])]
        access = spec.get("access")
        assert isinstance(access, list)
        if "write" not in access:
            continue
        prop = DreameVacuumProperty[name]
        if spec.get("format") == "bool":
            send_bool_values(device, fake, prop, mapping)
            continue
        for sample in _write_samples(spec):
            stored = family.convert_incoming(name, sample)
            force_property_set(device, prop, stored)
            assert fake.writes[-1][0] == mapping["siid"]
            assert fake.writes[-1][1] == mapping["piid"]
            assert fake.writes[-1][2] == family.convert_outgoing(name, stored)


def _assert_volume_span_and_blocked_map(
    device: DreameVacuumDevice, fake: FakeMiio, family: XiaomiModel
) -> None:
    """Assert volume covered 0 through 100 and map data produced no write."""
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
    assert device.set_property(DreameVacuumProperty.MAP_DATA, "blocked") is False
    assert len(fake.writes) == before


def _action_filenames(case: SpecCase) -> tuple[str, ...]:
    """Return the spec files whose mapped actions must take no parameters."""
    if case.action_spec_filenames:
        return case.action_spec_filenames
    return (case.spec_filename,)


def _assert_mapped_actions_take_no_input(case: SpecCase, family: XiaomiModel) -> None:
    """Assert every mapped action spec accepts an empty parameter list."""
    mapped_actions = mapped_addresses(family, "action")
    for filename in _action_filenames(case):
        for kind, siid, iid, spec in spec_items(filename):
            if kind == "action" and (siid, iid) in mapped_actions:
                assert not spec.get("in"), (filename, siid, iid)


def _invoke_each_mapped_action(
    device: DreameVacuumDevice, fake: FakeMiio, family: XiaomiModel
) -> None:
    """Call every mapped action, and expect auto-empty to stay unavailable."""
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


def _refuse_parameterized_actions(device: DreameVacuumDevice, fake: FakeMiio) -> None:
    """Assert Dreame actions that need parameters are not sent."""
    for action in _REFUSED_ACTIONS:
        before = len(fake.actions)
        with pytest.raises(InvalidActionException):
            device.call_action(action, {"in": [1]})
        assert len(fake.actions) == before


def _assert_each_status_wire(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    case: SpecCase,
    state: Mapping[str, int],
    charging: Mapping[str, int],
    error: Mapping[str, int],
) -> None:
    """Assert each published status wire becomes the expected shell state."""
    for wire, expected in case.state_after_read.items():
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


def _assert_shell_transitions(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    state: Mapping[str, int],
    charging: Mapping[str, int],
    error: Mapping[str, int],
) -> None:
    """Assert dock, idle, start, pause, resume, return, and error transitions."""
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


def _assert_one_control(
    case: SpecCase,
    family: XiaomiModel,
    control: XiaomiControl,
    current: Mapping[tuple[str, int, int], Mapping[str, object]],
    previous: Mapping[tuple[str, int, int], Mapping[str, object]] | None,
) -> None:
    """Assert one control against the current spec and, when present, the previous."""
    if control.property_name:
        spec = current[("property", *property_address(family, control.property_name))]
        assert_control_options(control, spec)
        return
    kind = "action" if control.aiid is not None else "property"
    pair = (
        control.siid,
        control.aiid if control.aiid is not None else control.piid,
    )
    assert (kind, pair[0], pair[1]) in current
    assert_control_matches_spec(control, current[(kind, pair[0], pair[1])])
    if previous is None:
        return
    if pair in case.version_only_controls:
        assert (kind, pair[0], pair[1]) not in previous
        return
    assert_control_matches_spec(control, previous[(kind, pair[0], pair[1])])


def _exercise_one_control(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    specs: Mapping[tuple[str, int, int], Mapping[str, object]],
    control: XiaomiControl,
) -> None:
    """Read and, when writable, send every sample for one control."""
    if control.aiid is not None:
        spec = specs[("action", control.siid, control.aiid)]
        assert not spec.get("in")
        invoke_control(device, control)
        assert fake.actions[-1] == (control.siid, control.aiid)
        assert fake.action_inputs[-1] == []
        return
    if control.property_name:
        _send_named_property_options(device, fake, family, control)
        return
    direct = specs[("property", control.siid, control.piid)]
    for sample in spec_samples(direct, full_range_limit=_CONTROL_SAMPLE_LIMIT):
        fake.set_value(control.siid, control.piid, sample)
        family.refresh_controls(device)
        assert read_control(device, control) == sample
    if not control.writable:
        return
    for sample in spec_samples(direct, full_range_limit=_CONTROL_SAMPLE_LIMIT):
        write_control(device, control, sample)
        assert fake.writes[-1] == (control.siid, control.piid, sample)
        assert read_control(device, control) == sample


def _write_samples(spec: Mapping[str, object]) -> list[object]:
    """Return writable samples, expanding a range before the generic samples."""
    bounds = _range_bounds(spec)
    if bounds is not None:
        start, end, step = bounds
        if (end - start) // step <= _WRITE_SAMPLE_LIMIT:
            return list(range(start, end + 1, step))
    return spec_samples(spec)


def _range_bounds(spec: Mapping[str, object]) -> tuple[int, int, int] | None:
    """Return start, end, and step when the spec publishes a three-item range."""
    bounds = spec.get("value-range")
    if not isinstance(bounds, list) or len(bounds) != 3:
        return None
    start, end, step = bounds
    assert isinstance(start, int)
    assert isinstance(end, int)
    assert isinstance(step, int)
    return start, end, step


def _send_named_property_options(
    device: DreameVacuumDevice,
    fake: FakeMiio,
    family: XiaomiModel,
    control: XiaomiControl,
) -> None:
    """Send each option of a control that reuses a Dreame property."""
    name = control.property_name
    assert name
    prop = DreameVacuumProperty[name]
    mapping = family.property_overrides[name]
    for value, _slug in control.options:
        force_property_set(device, prop, value)
        assert fake.writes[-1] == (mapping["siid"], mapping["piid"], value)


def _refuse_write(*_args: object, **_kwargs: object) -> list[dict[str, int]]:
    return [{"code": -1}]


def _refuse_action(*_args: object, **_kwargs: object) -> dict[str, int]:
    return {"code": -1}


def _refuse_read(*_args: object, **_kwargs: object) -> None:
    return None
