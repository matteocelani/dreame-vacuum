"""Spec coverage for xiaomi.vacuum.ov31gl, the Xiaomi Robot Vacuum 5."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi.mapping import MODEL_ROBOT_VACUUM_5
import pytest
from tests.xiaomi.spec_helpers import (
    SpecCase,
    assert_controls_match_spec,
    assert_spec_is_fully_classified,
    exercise_control_values,
    exercise_mapped_actions,
    exercise_mapped_property_reads,
    exercise_rejected_control_traffic,
    exercise_status_wires,
    exercise_writable_values,
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
    22: DreameVacuumState.WASHING,
    23: DreameVacuumState.CHARGING_COMPLETED,
    24: DreameVacuumState.RETURNING,
}

_V2_ONLY_CONTROLS: Final[set[tuple[int, int]]] = {(20, 9), (20, 11)}

_CASE = SpecCase(
    model=MODEL_ROBOT_VACUUM_5,
    device_name="Vacuum 5",
    spec_filename="ov31gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={
        "ov31gl.json": (132, 103),
        "ov31gl_v1.json": (130, 100),
    },
    version_only_controls=frozenset(_V2_ONLY_CONTROLS),
    action_spec_filenames=("ov31gl.json", "ov31gl_v1.json"),
    previous_spec_filename="ov31gl_v1.json",
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_both_spec_versions_are_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason."""
    assert_spec_is_fully_classified(_CASE)


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
    """Read every spec sample and send every writable value, including 0 through 255."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)
