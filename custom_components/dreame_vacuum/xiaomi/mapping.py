"""MIoT maps and value conversion for Xiaomi S20+ and X20 Max."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Final

from .exceptions import XiaomiTransportException
from .transport import MiioPropertyTransport

MODEL_S20_PLUS: Final = "xiaomi.vacuum.b108gl"
MODEL_X20_MAX: Final = "xiaomi.vacuum.d109gl"
_ONE_INDEXED_PROPERTIES: Final[frozenset[str]] = frozenset(
    {"CLEANING_MODE", "SUCTION_LEVEL"}
)


class _StoredState(IntEnum):
    """Dreame state codes stored after Xiaomi values are converted."""

    SWEEPING = 1
    IDLE = 2
    PAUSED = 3
    ERROR = 4
    RETURNING = 5
    CHARGING = 6
    MOPPING = 7
    DRYING = 8
    WASHING = 9
    RETURNING_TO_WASH = 10
    BUILDING = 11
    SWEEPING_AND_MOPPING = 12
    CHARGING_COMPLETED = 13
    UPGRADING = 14
    WASHING_PAUSED = 21
    REMOTE_CONTROL = 23
    STATION_CLEANING = 30


class _StoredTask(IntEnum):
    """Dreame task-status codes derived for these two models."""

    COMPLETED = 0
    AUTO_CLEANING = 1
    ZONE_CLEANING = 2
    SEGMENT_CLEANING = 3
    SPOT_CLEANING = 4
    FAST_MAPPING = 5
    AUTO_CLEANING_PAUSED = 6


class _StoredCharging(IntEnum):
    """Dreame charging-status codes that mean the robot is docked."""

    CHARGING = 1
    CHARGING_COMPLETED = 3


class _S20PlusState(IntEnum):
    """Wire status codes for xiaomi.vacuum.b108gl."""

    IDLE = 1
    CHARGING = 2
    BREAK_CHARGING = 3
    SWEEPING = 4
    PAUSED = 5
    RETURNING = 6
    REMOTE = 7
    CHARGED = 8
    MAPPING = 9
    UPDATING = 10


class _S20PlusTask(IntEnum):
    """Wire sweep-type codes for xiaomi.vacuum.b108gl."""

    GLOBAL = 1
    AREA = 4
    MAPPING = 5
    GO_CHARGING = 6
    REMOTE = 7
    SELECT_ROOM = 8
    CUSTOM = 9


class _X20MaxState(IntEnum):
    """Wire status codes for xiaomi.vacuum.d109gl."""

    IDLE = 1
    CHARGING = 2
    BREAK_CHARGING = 3
    SWEEPING = 4
    PAUSED = 5
    RETURNING = 6
    GO_WASH = 7
    REMOTE = 8
    CHARGED = 9
    BUILDING = 10
    UPDATING = 11
    MULTI_TASK_STATION = 12
    MULTI_TASK_RECHARGE = 13
    STATION_WORKING = 14
    ERROR = 15
    SWEEPING_AND_MOPPING = 16
    MOPPING = 17
    MAPPING_PAUSE = 18
    GO_CHARGE_BREAK = 19
    WASH_BREAK = 20
    GO_CHARGE_BUILDING = 21


class _X20MaxTask(IntEnum):
    """Wire sweep-type codes for xiaomi.vacuum.d109gl."""

    GLOBAL = 1
    ZONE = 2
    AREA = 3
    EDGE = 4
    CUSTOM = 5
    POINT = 6
    CUSTOM_AREA = 7


_S20_PLUS_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "TASK_STATUS": {"siid": 2, "piid": 4},
    "CLEANING_TIME": {"siid": 2, "piid": 6},
    "CLEANED_AREA": {"siid": 2, "piid": 5},
    "SUCTION_LEVEL": {"siid": 2, "piid": 8},
    "WATER_VOLUME": {"siid": 2, "piid": 9},
    "WATER_TANK": {"siid": 6, "piid": 1},
    "CLEANING_MODE": {"siid": 2, "piid": 3},
    "CARPET_BOOST": {"siid": 6, "piid": 6},
    "CARPET_CLEANING": {"siid": 2, "piid": 20},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "RESUME_CLEANING": {"siid": 6, "piid": 11},
    "DND": {"siid": 6, "piid": 3},
    "MAP_DATA": {"siid": 7, "piid": 1},
    "OBJECT_NAME": {"siid": 7, "piid": 1},
    "OLD_MAP_DATA": {"siid": 7, "piid": 2},
    "MAP_LIST": {"siid": 7, "piid": 3},
    "MULTI_FLOOR_MAP": {"siid": 7, "piid": 5},
    "MAP_SAVING": {"siid": 7, "piid": 9},
    "VOLUME": {"siid": 4, "piid": 2},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 8, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 8, "piid": 2},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 9, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 9, "piid": 2},
    "FILTER_TIME_LEFT": {"siid": 10, "piid": 1},
    "FILTER_LEFT": {"siid": 10, "piid": 2},
    "MOP_PAD_LEFT": {"siid": 11, "piid": 2},
    "MOP_PAD_TIME_LEFT": {"siid": 11, "piid": 1},
    "SCHEDULE": {"siid": 6, "piid": 5},
    "RELOCATION_STATUS": {"siid": 6, "piid": 9},
    "CLEANING_PROPERTIES": {"siid": 6, "piid": 12},
    "FAULTS": {"siid": 6, "piid": 13},
}

_S20_PLUS_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 6},
    "START_CUSTOM": {"siid": 6, "aiid": 7},
    "LOCATE": {"siid": 6, "aiid": 6},
    "RESET_MAIN_BRUSH": {"siid": 8, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 9, "aiid": 1},
    "RESET_FILTER": {"siid": 10, "aiid": 1},
    # siid 6 aiid 1 is start-vacuum on this model, not a map request.
    "REQUEST_MAP": {},
    "UPDATE_MAP_DATA": {},
    "WIFI_MAP": {},
}

_X20_MAX_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 2},
    "ERROR": {"siid": 2, "piid": 3},
    "CLEANING_MODE": {"siid": 2, "piid": 4},
    "TASK_STATUS": {"siid": 2, "piid": 5},
    "CLEANED_AREA": {"siid": 2, "piid": 6},
    "CLEANING_TIME": {"siid": 2, "piid": 7},
    "SUCTION_LEVEL": {"siid": 2, "piid": 9},
    "WATER_VOLUME": {"siid": 2, "piid": 10},
    "WATER_TANK": {"siid": 2, "piid": 11},
    "CARPET_BOOST": {"siid": 2, "piid": 20},
    "CARPET_CLEANING": {"siid": 2, "piid": 73},
    "RESUME_CLEANING": {"siid": 2, "piid": 23},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "MAP_DATA": {"siid": 10, "piid": 1},
    "OBJECT_NAME": {"siid": 10, "piid": 1},
    "OLD_MAP_DATA": {"siid": 10, "piid": 2},
    "MAP_LIST": {"siid": 10, "piid": 5},
    "MULTI_FLOOR_MAP": {"siid": 10, "piid": 10},
    "MAP_SAVING": {"siid": 10, "piid": 11},
    "DND": {"siid": 11, "piid": 1},
    "SCHEDULE": {"siid": 2, "piid": 19},
    "MAIN_BRUSH_LEFT": {"siid": 12, "piid": 1},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 12, "piid": 2},
    "SIDE_BRUSH_LEFT": {"siid": 13, "piid": 1},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 13, "piid": 2},
    "FILTER_LEFT": {"siid": 14, "piid": 1},
    "FILTER_TIME_LEFT": {"siid": 14, "piid": 2},
    "MOP_PAD_LEFT": {"siid": 9, "piid": 1},
    "MOP_PAD_TIME_LEFT": {"siid": 9, "piid": 2},
    "RELOCATION_STATUS": {"siid": 2, "piid": 26},
    "FAULTS": {"siid": 2, "piid": 66},
    "CLEANING_PROPERTIES": {"siid": 2, "piid": 40},
}

_X20_MAX_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 7},
    "START_CUSTOM": {"siid": 2, "aiid": 9},
    "LOCATE": {"siid": 6, "aiid": 1},
    "RESET_MAIN_BRUSH": {"siid": 12, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 13, "aiid": 1},
    "RESET_FILTER": {"siid": 14, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 9, "aiid": 1},
    "REQUEST_MAP": {"siid": 10, "aiid": 7},
    "UPDATE_MAP_DATA": {},
    "WIFI_MAP": {},
}

_DOCKED_TASK_STATES: Final[frozenset[int]] = frozenset(
    {
        int(_StoredState.IDLE),
        int(_StoredState.CHARGING),
        int(_StoredState.CHARGING_COMPLETED),
        int(_StoredState.RETURNING),
        int(_StoredState.WASHING),
        int(_StoredState.RETURNING_TO_WASH),
        int(_StoredState.DRYING),
        int(_StoredState.STATION_CLEANING),
        int(_StoredState.ERROR),
    }
)
_PAUSED_TASK_STATES: Final[frozenset[int]] = frozenset(
    {int(_StoredState.PAUSED), int(_StoredState.WASHING_PAUSED)}
)
_ACTIVE_TASK_STATES: Final[frozenset[int]] = frozenset(
    {
        int(_StoredState.SWEEPING),
        int(_StoredState.MOPPING),
        int(_StoredState.SWEEPING_AND_MOPPING),
    }
)


@dataclass(frozen=True, slots=True)
class XiaomiModel:
    """MIoT identity and value conversion for one Xiaomi vacuum."""

    model: str
    property_overrides: dict[str, dict[str, int]]
    action_overrides: dict[str, dict[str, int]]
    state_by_wire: dict[int, int]
    task_by_wire: dict[int, int]
    is_simple_cleaning_mode: bool = True
    should_correct_docked_activity: bool = True

    def convert_incoming(self, property_name: str, value: object) -> object:
        """Map a raw property value into the Dreame value domain."""
        number = _as_int(value)
        if number is None:
            return value
        if property_name == "STATE":
            mapped = self.state_by_wire.get(number)
            return number if mapped is None else mapped
        if property_name == "TASK_STATUS":
            mapped = self.task_by_wire.get(number)
            return number if mapped is None else mapped
        if property_name in _ONE_INDEXED_PROPERTIES and number > 0:
            return number - 1
        return number

    def convert_outgoing(self, property_name: str, value: object) -> object:
        """Map a Dreame value to the integer the robot expects on the wire."""
        if property_name not in _ONE_INDEXED_PROPERTIES or isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value + 1
        return value

    def task_status_code(self, state: object, charging: object) -> int:
        """Derive task status from state, because sweep-type stays set while docked."""
        charging_code = _as_int(charging)
        if charging_code in (
            int(_StoredCharging.CHARGING),
            int(_StoredCharging.CHARGING_COMPLETED),
        ):
            return int(_StoredTask.COMPLETED)
        state_code = _as_int(state)
        if state_code in _DOCKED_TASK_STATES:
            return int(_StoredTask.COMPLETED)
        if state_code in _PAUSED_TASK_STATES:
            return int(_StoredTask.AUTO_CLEANING_PAUSED)
        if state_code in _ACTIVE_TASK_STATES:
            return int(_StoredTask.AUTO_CLEANING)
        return int(_StoredTask.COMPLETED)

    def build_property_transport(
        self, host: str, token: str
    ) -> MiioPropertyTransport | None:
        """Build a local property transport, or None when the cloud path remains."""
        # None is the existing cloud path. An invalid token must not raise into Dreame.
        if not host or not token:
            return None
        try:
            return MiioPropertyTransport(host, token)
        except XiaomiTransportException:
            return None


def resolve_family(model: str) -> XiaomiModel | None:
    """Return the Xiaomi codec for S20+ or X20 Max, otherwise None."""
    return _FAMILIES.get(model)


def _as_int(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _wire_map(pairs: tuple[tuple[IntEnum, IntEnum], ...]) -> dict[int, int]:
    return {int(wire): int(stored) for wire, stored in pairs}


_S20_PLUS_STATES: Final[dict[int, int]] = _wire_map(
    (
        (_S20PlusState.IDLE, _StoredState.IDLE),
        (_S20PlusState.CHARGING, _StoredState.CHARGING),
        (_S20PlusState.BREAK_CHARGING, _StoredState.CHARGING),
        (_S20PlusState.SWEEPING, _StoredState.SWEEPING),
        (_S20PlusState.PAUSED, _StoredState.PAUSED),
        (_S20PlusState.RETURNING, _StoredState.RETURNING),
        (_S20PlusState.REMOTE, _StoredState.REMOTE_CONTROL),
        (_S20PlusState.CHARGED, _StoredState.CHARGING_COMPLETED),
        (_S20PlusState.MAPPING, _StoredState.BUILDING),
        (_S20PlusState.UPDATING, _StoredState.UPGRADING),
    )
)
_S20_PLUS_TASKS: Final[dict[int, int]] = _wire_map(
    (
        (_S20PlusTask.GLOBAL, _StoredTask.AUTO_CLEANING),
        (_S20PlusTask.AREA, _StoredTask.ZONE_CLEANING),
        (_S20PlusTask.MAPPING, _StoredTask.FAST_MAPPING),
        (_S20PlusTask.GO_CHARGING, _StoredTask.COMPLETED),
        (_S20PlusTask.REMOTE, _StoredTask.COMPLETED),
        (_S20PlusTask.SELECT_ROOM, _StoredTask.SEGMENT_CLEANING),
        (_S20PlusTask.CUSTOM, _StoredTask.SPOT_CLEANING),
    )
)
_X20_MAX_STATES: Final[dict[int, int]] = _wire_map(
    (
        (_X20MaxState.IDLE, _StoredState.IDLE),
        (_X20MaxState.CHARGING, _StoredState.CHARGING),
        (_X20MaxState.BREAK_CHARGING, _StoredState.CHARGING),
        (_X20MaxState.SWEEPING, _StoredState.SWEEPING),
        (_X20MaxState.PAUSED, _StoredState.PAUSED),
        (_X20MaxState.RETURNING, _StoredState.RETURNING),
        (_X20MaxState.GO_WASH, _StoredState.RETURNING_TO_WASH),
        (_X20MaxState.REMOTE, _StoredState.REMOTE_CONTROL),
        (_X20MaxState.CHARGED, _StoredState.CHARGING_COMPLETED),
        (_X20MaxState.BUILDING, _StoredState.BUILDING),
        (_X20MaxState.UPDATING, _StoredState.UPGRADING),
        (_X20MaxState.MULTI_TASK_STATION, _StoredState.STATION_CLEANING),
        (_X20MaxState.MULTI_TASK_RECHARGE, _StoredState.CHARGING),
        (_X20MaxState.STATION_WORKING, _StoredState.STATION_CLEANING),
        (_X20MaxState.ERROR, _StoredState.ERROR),
        (_X20MaxState.SWEEPING_AND_MOPPING, _StoredState.SWEEPING_AND_MOPPING),
        (_X20MaxState.MOPPING, _StoredState.MOPPING),
        (_X20MaxState.MAPPING_PAUSE, _StoredState.PAUSED),
        (_X20MaxState.GO_CHARGE_BREAK, _StoredState.RETURNING),
        (_X20MaxState.WASH_BREAK, _StoredState.RETURNING_TO_WASH),
        (_X20MaxState.GO_CHARGE_BUILDING, _StoredState.BUILDING),
    )
)
_X20_MAX_TASKS: Final[dict[int, int]] = _wire_map(
    (
        (_X20MaxTask.GLOBAL, _StoredTask.AUTO_CLEANING),
        (_X20MaxTask.ZONE, _StoredTask.ZONE_CLEANING),
        (_X20MaxTask.AREA, _StoredTask.SPOT_CLEANING),
        (_X20MaxTask.EDGE, _StoredTask.ZONE_CLEANING),
        (_X20MaxTask.CUSTOM, _StoredTask.SEGMENT_CLEANING),
        (_X20MaxTask.POINT, _StoredTask.SPOT_CLEANING),
        (_X20MaxTask.CUSTOM_AREA, _StoredTask.ZONE_CLEANING),
    )
)

_FAMILIES: Final[dict[str, XiaomiModel]] = {
    MODEL_S20_PLUS: XiaomiModel(
        model=MODEL_S20_PLUS,
        property_overrides=_S20_PLUS_PROPERTIES,
        action_overrides=_S20_PLUS_ACTIONS,
        state_by_wire=_S20_PLUS_STATES,
        task_by_wire=_S20_PLUS_TASKS,
    ),
    MODEL_X20_MAX: XiaomiModel(
        model=MODEL_X20_MAX,
        property_overrides=_X20_MAX_PROPERTIES,
        action_overrides=_X20_MAX_ACTIONS,
        state_by_wire=_X20_MAX_STATES,
        task_by_wire=_X20_MAX_TASKS,
    ),
}
