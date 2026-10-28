"""Spec coverage for xiaomi.vacuum.d102gl, the Xiaomi Robot Vacuum X20 Pro."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_X20_PRO
import pytest
from tests.xiaomi.spec_helpers import (
    SpecCase,
    assert_controls_have_english_names,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_rejected_control_traffic,
    exercise_status_wires,
    exercise_writable_values,
    mapped_addresses,
    normalize_spec,
    require_family,
    spec_index,
)

_PROPERTY_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
}

_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
}

_STATE_AFTER_READ: Final[dict[int, DreameVacuumState]] = {
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
}

_CASE = SpecCase(
    model=MODEL_X20_PRO,
    device_name="X20 Pro",
    spec_filename="d102gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"d102gl.json": (99, 84)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d102gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 46,
        "needs council": 23,
        "no ha meaning": 10,
    },
    action_spec_filenames=("d102gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    The instances list publishes version 1 only. Version 2 is not released.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("d102gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    family = require_family(MODEL_X20_PRO)
    assert wires == [*range(1, 22)]
    assert set(wires) == set(_STATE_AFTER_READ)
    assert set(family.state_by_wire) == set(wires)


def test_every_control_has_an_english_name() -> None:
    """Each control key and option slug has an English translation."""
    assert_controls_have_english_names(_CASE)


def test_every_mapped_property_reads_each_spec_value(socket_enabled: None) -> None:
    del socket_enabled
    exercise_mapped_property_reads(_CASE)


def test_every_writable_value_is_sent_and_unmapped_writes_are_not(
    socket_enabled: None,
) -> None:
    del socket_enabled
    exercise_writable_values(_CASE)


def test_every_mapped_action_is_invoked_or_refused_without_parameters(
    socket_enabled: None,
) -> None:
    del socket_enabled
    exercise_mapped_actions(_CASE)


def test_every_status_wire_reaches_the_shell_state(socket_enabled: None) -> None:
    del socket_enabled
    exercise_status_wires(_CASE)


def test_controls_match_the_spec() -> None:
    """Each control's options, range, and access follow the spec that defines it."""
    assert_controls_match_spec(_CASE)


def test_every_control_value_is_read_or_sent(socket_enabled: None) -> None:
    """Read every spec sample and send every writable value."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)


def test_published_spec_matches_x20_max_except_the_known_gaps() -> None:
    """Version 1 overlaps the X20 Max spec except swing, wash area, and extras."""
    current = spec_index("d102gl.json")
    x20_max = spec_index("d109gl.json")
    assert set(current) - set(x20_max) == {
        ("property", 2, 55),
        ("property", 2, 68),
    }
    assert set(x20_max) - set(current) == {
        ("property", 2, 79),
        ("property", 2, 80),
        ("property", 2, 81),
        ("property", 2, 82),
        ("property", 2, 83),
        ("property", 2, 84),
        ("property", 20, 7),
        ("property", 20, 8),
    }
    changed = {("property", 2, 61)}
    codes = ("d102gl", "d109gl")
    for key in (set(current) & set(x20_max)) - changed:
        assert normalize_spec(current[key], codes) == normalize_spec(
            x20_max[key], codes
        ), key
    wash_area = current[("property", 2, 61)]
    assert _values(wash_area) == [0, 1, 2]
    edge = current[("property", 2, 68)]
    assert _values(edge) == [1, 2]
    assert [item.strip() for item in _descriptions(edge)] == ["Every Time", "7 Sweeps"]


def test_unpublished_station_addresses_are_not_mapped() -> None:
    """Addresses the X20 Max spec adds, and map actions, stay off the wire."""
    family = require_family(MODEL_X20_PRO)
    properties = mapped_addresses(family, "property")
    actions = mapped_addresses(family, "action")
    for pair in (
        (2, 79),
        (2, 80),
        (2, 81),
        (2, 82),
        (2, 83),
        (2, 84),
        (2, 85),
        (10, 1),
        (20, 7),
    ):
        assert pair not in properties
    for pair in ((2, 17), (2, 33), (10, 1), (16, 1)):
        assert pair not in actions
    wash = next(
        control for control in family.controls if control.key == "xiaomi_mop_wash_area"
    )
    assert [value for value, _slug in wash.options] == [0, 1, 2]
    edge = next(
        control
        for control in family.controls
        if control.key == "xiaomi_edge_sweep_frequency"
    )
    assert [(value, slug) for value, slug in edge.options] == [
        (1, "every_time"),
        (2, "seven_sweeps"),
    ]


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]
