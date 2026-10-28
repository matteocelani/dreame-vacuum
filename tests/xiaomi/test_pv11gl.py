"""Spec coverage for xiaomi.vacuum.pv11gl, the Xiaomi Robot Vacuum 6 Max."""

from __future__ import annotations

from typing import Final

from custom_components.dreame_vacuum.dreame.types import DreameVacuumState
from custom_components.dreame_vacuum.xiaomi import MODEL_ROBOT_VACUUM_6_MAX
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
    (2, 56): "map: AI objects.",
    (2, 57): "map: furniture.",
    (2, 58): "map: carpet objects.",
    (2, 65): "map: vacuum route is not readable and is map geometry.",
    (2, 67): "no ha meaning: action result is a command echo.",
    (2, 70): "needs council: plugin reminder text needs a text entity.",
    (2, 99): "map: sill geometry.",
    (2, 102): "map: automation furniture.",
    (2, 103): "map: hidden zones stay unmapped until map support.",
    (11, 2): "needs council: DND time is one packed integer, not a start and end.",
    (15, 1): "needs council: target voice id encoding is not a Dreame voice property.",
    (15, 5): "no ha meaning: voice url is neither readable nor writable.",
    (15, 6): "no ha meaning: voice common params are neither readable nor writable.",
    (20, 1): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 2): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 3): "needs council: unnamed readable string.",
    (20, 4): "no ha meaning: self-check items are neither readable nor writable.",
    (20, 5): "needs council: unnamed readable string.",
    (20, 6): "needs council: unnamed writable field has no published meaning.",
    (20, 10): "needs council: unnamed writable field has no published meaning.",
    (20, 12): "no ha meaning: unnamed field is neither readable nor writable.",
    (20, 13): "needs council: unnamed writable field has no published meaning.",
    (20, 14): "needs council: unnamed readable string.",
    (20, 15): "needs council: unnamed readable string.",
    (21, 7): "no ha meaning: stream common params are neither readable nor writable.",
    (22, 1): "no ha meaning: self-check items are neither readable nor writable.",
}

_ACTION_REASONS: Final[dict[tuple[int, int], str]] = {
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
    (2, 52): "map: skip cleaning takes a room-id parameter.",
    (2, 53): "map: final cleaning takes a room-id parameter.",
    (2, 54): "map: temporary room cleaning takes a room-id parameter.",
    (2, 55): "map: temporary zone cleaning takes a zone parameter.",
    (2, 56): "map: furniture cleaning takes a map parameter.",
    (2, 60): "needs council: operating an AI object takes an opaque parameter.",
    (2, 61): "map: AI picture objects stay unmapped until map support.",
    (2, 62): "needs council: common-object clean takes an object parameter.",
    (2, 65): "map: rotating the map takes a parameter and is map geometry.",
    (15, 1): "needs council: voice download takes a pack url.",
    (15, 2): "no ha meaning: download status is already the mapped property.",
    (20, 1): "map: history objects stay unmapped until map support.",
    (20, 2): "needs council: user-defined info takes an opaque parameter.",
    (20, 3): "map: stopping a map upload stays unmapped until map support.",
    (
        20,
        4,
    ): "no ha meaning: the Xiaoai bind id is a diagnostic fetch, not a user control.",
    (20, 5): "needs council: reading a schedule takes an opaque parameter.",
    (20, 6): "needs council: switching a schedule takes an opaque parameter.",
    (
        20,
        7,
    ): "needs council: lidar control takes a parameter and must not enable map support.",
    (20, 8): "needs council: starting a patrol takes an opaque parameter.",
    (20, 10): "needs council: reading a language pack takes an opaque parameter.",
    (20, 12): "needs council: acknowledging a check result takes an opaque parameter.",
    (20, 13): "needs council: reading the check result takes an opaque parameter.",
    (20, 14): "needs council: leaving check mode takes an opaque parameter.",
    (20, 15): "needs council: starting a check task takes an opaque parameter.",
    (21, 4): "needs council: entering the video page takes an opaque parameter.",
    (21, 5): "no ha meaning: video status is a diagnostic fetch, not a user control.",
    (
        21,
        6,
    ): "needs council: setting a video password must not be sent as a raw action.",
    (
        21,
        7,
    ): "needs council: verifying a video password must not be sent as a raw action.",
    (
        21,
        8,
    ): "needs council: forgot-password changes a video credential and has no confirmation flow.",
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
    24: DreameVacuumState.RETURNING,
    25: DreameVacuumState.UNKNOWN,
    26: DreameVacuumState.CLEAN_SUMMON,
    27: DreameVacuumState.SWEEPING,
}

_CASE = SpecCase(
    model=MODEL_ROBOT_VACUUM_6_MAX,
    device_name="Robot Vacuum 6 Max",
    spec_filename="pv11gl.json",
    property_reasons=_PROPERTY_REASONS,
    action_reasons=_ACTION_REASONS,
    state_after_read=_STATE_AFTER_READ,
    classification_counts={"pv11gl.json": (150, 125)},
    spec_type="urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv11gl:1",
    reason_prefix_counts={
        "identity": 5,
        "map": 59,
        "needs council": 45,
        "no ha meaning": 16,
    },
    absent_items=(
        ("action", 2, 66),
        ("action", 20, 16),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
    ),
    action_spec_filenames=("pv11gl.json",),
)

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_the_published_spec_is_fully_classified() -> None:
    """Each spec item is mapped or has one explicit omission reason.

    home.miot-spec.com lists released version 1 only. miot-spec.org's released
    instance list matches. Xiaomi's compliance list names this model PV11GL.
    """
    assert_spec_is_fully_classified(_CASE)


def test_every_published_status_wire_has_a_shell_state() -> None:
    """The state table covers the status value list and no extra wire."""
    listed = spec_index("pv11gl.json")[("property", 2, 2)].get("value-list")
    assert isinstance(listed, list)
    wires = [item["value"] for item in listed if isinstance(item, dict)]
    assert wires == [*range(1, 22), 24, 25, 26, 27]
    assert set(wires) == set(_STATE_AFTER_READ)


def test_video_password_actions_are_not_mapped() -> None:
    """Password actions stay off the wire. There is no confirmation flow."""
    actions = mapped_addresses(require_family(MODEL_ROBOT_VACUUM_6_MAX), "action")
    assert (21, 6) not in actions
    assert (21, 7) not in actions
    assert (21, 8) not in actions


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
    """Read every spec sample and send every writable value, including 0 through 255."""
    del socket_enabled
    exercise_control_values(_CASE)


def test_rejected_control_traffic_is_not_stored(socket_enabled: None) -> None:
    """A refused read or write leaves the stored value unchanged."""
    del socket_enabled
    exercise_rejected_control_traffic(_CASE)


def test_published_spec_matches_robot_vacuum_6_except_station_hardware() -> None:
    """Version 1 adds mop, detergent, camera, and stream items Robot Vacuum 6 lacks."""
    current = spec_index("pv11gl.json")
    vacuum_6 = spec_index("pv32gl.json")
    assert set(current) - set(vacuum_6) == {
        ("action", 2, 19),
        ("action", 2, 21),
        ("action", 2, 22),
        ("action", 9, 1),
        ("action", 18, 1),
        ("action", 20, 7),
        ("action", 20, 8),
        ("action", 20, 11),
        ("action", 20, 12),
        ("action", 20, 13),
        ("action", 20, 14),
        ("action", 20, 15),
        ("action", 21, 4),
        ("action", 21, 5),
        ("action", 21, 6),
        ("action", 21, 7),
        ("action", 21, 8),
        ("property", 2, 44),
        ("property", 2, 46),
        ("property", 2, 47),
        ("property", 2, 48),
        ("property", 2, 59),
        ("property", 2, 60),
        ("property", 2, 71),
        ("property", 2, 76),
        ("property", 2, 78),
        ("property", 2, 92),
        ("property", 2, 93),
        ("property", 2, 94),
        ("property", 2, 95),
        ("property", 2, 97),
        ("property", 2, 98),
        ("property", 2, 107),
        ("property", 9, 1),
        ("property", 9, 2),
        ("property", 18, 1),
        ("property", 18, 2),
        ("property", 18, 3),
        ("property", 18, 4),
        ("property", 20, 9),
        ("property", 20, 10),
        ("property", 20, 11),
        ("property", 20, 12),
        ("property", 20, 13),
        ("property", 20, 14),
        ("property", 20, 15),
        ("property", 21, 2),
        ("property", 21, 4),
        ("property", 21, 5),
        ("property", 21, 6),
        ("property", 21, 7),
        ("property", 21, 8),
    }
    assert set(vacuum_6) - set(current) == {
        ("action", 2, 66),
        ("action", 20, 16),
        ("property", 2, 104),
        ("property", 2, 105),
        ("property", 2, 106),
        ("property", 23, 1),
        ("property", 23, 2),
        ("property", 23, 3),
    }
    changed = {
        ("property", 2, 2),
        ("property", 2, 61),
    }
    type_only = {
        ("action", 20, 9),
        ("action", 20, 10),
        ("property", 13, 1),
        ("property", 14, 1),
        ("property", 14, 2),
    }
    codes = ("pv11gl", "pv32gl")
    for key in (set(current) & set(vacuum_6)) - changed - type_only:
        assert normalize_spec(current[key], codes) == normalize_spec(
            vacuum_6[key], codes
        ), key
    for key in type_only:
        left = normalize_spec(current[key], codes)
        right = normalize_spec(vacuum_6[key], codes)
        assert isinstance(left, dict)
        assert isinstance(right, dict)
        left_fields = dict(left)
        right_fields = dict(right)
        left_type = left_fields.pop("type")
        right_type = right_fields.pop("type")
        left_fields.pop("gatt-access", None)
        right_fields.pop("gatt-access", None)
        assert left_fields == right_fields
        assert (
            str(left_type).split(":xiaomi-")[0] == str(right_type).split(":xiaomi-")[0]
        )
    status = current[("property", 2, 2)].get("value-list")
    assert isinstance(status, list)
    assert [item["value"] for item in status if isinstance(item, dict)] == [
        *range(1, 22),
        24,
        25,
        26,
        27,
    ]
    area = current[("property", 2, 61)]
    other_area = vacuum_6[("property", 2, 61)]
    assert _values(area) == _values(other_area)
    assert [item.replace("  ", " ") for item in _descriptions(area)] == _descriptions(
        other_area
    )


def _values(spec: dict[str, object]) -> list[object]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [item["value"] for item in listed if isinstance(item, dict)]


def _descriptions(spec: dict[str, object]) -> list[str]:
    listed = spec.get("value-list")
    assert isinstance(listed, list)
    return [str(item["description"]) for item in listed if isinstance(item, dict)]
