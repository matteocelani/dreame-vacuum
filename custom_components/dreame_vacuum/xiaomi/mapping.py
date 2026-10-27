"""MIoT maps and value conversion for Xiaomi vacuum models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import IntEnum
from typing import Final

from .exceptions import XiaomiTransportException
from .transport import MiioPropertyTransport

MODEL_S20_PLUS: Final = "xiaomi.vacuum.b108gl"
MODEL_X20_MAX: Final = "xiaomi.vacuum.d109gl"
MODEL_ROBOT_VACUUM_5: Final = "xiaomi.vacuum.ov31gl"
_ONE_INDEXED_PROPERTIES: Final[frozenset[str]] = frozenset(
    {"CLEANING_MODE", "SUCTION_LEVEL"}
)
_CHARGING: Final = 1
_NOT_CHARGING: Final = 2
_NOT_CHARGEABLE: Final = 3


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


class _RobotVacuum5State(IntEnum):
    """Status codes xiaomi.vacuum.ov31gl adds after the X20 Max list."""

    STATION_ASSISTING = 22
    STATION_ASSISTED = 23
    RETURNING_DURING_ASSIST = 24


class _RobotVacuum5Task(IntEnum):
    """Sweep-type codes xiaomi.vacuum.ov31gl adds after the X20 Max list."""

    APPOINTMENT = 8
    LINKAGE = 9
    FAST_MAPPING = 10
    AI_HOSTING = 11


_S20_PLUS_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    "STATE": {"siid": 2, "piid": 1},
    "ERROR": {"siid": 2, "piid": 2},
    "CLEANING_MODE": {"siid": 2, "piid": 3},
    "TASK_STATUS": {"siid": 2, "piid": 4},
    "CLEANED_AREA": {"siid": 2, "piid": 5},
    "CLEANING_TIME": {"siid": 2, "piid": 6},
    "SUCTION_LEVEL": {"siid": 2, "piid": 8},
    "WATER_VOLUME": {"siid": 2, "piid": 9},
    "CARPET_CLEANING": {"siid": 2, "piid": 20},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "CHARGING_STATUS": {"siid": 3, "piid": 2},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "WATER_TANK": {"siid": 6, "piid": 1},
    "DND": {"siid": 6, "piid": 3},
    "SCHEDULE": {"siid": 6, "piid": 5},
    "CARPET_BOOST": {"siid": 6, "piid": 6},
    "RELOCATION_STATUS": {"siid": 6, "piid": 9},
    "RESUME_CLEANING": {"siid": 6, "piid": 11},
    "FAULTS": {"siid": 6, "piid": 13},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 8, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 8, "piid": 2},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 9, "piid": 1},
    "SIDE_BRUSH_LEFT": {"siid": 9, "piid": 2},
    "FILTER_TIME_LEFT": {"siid": 10, "piid": 1},
    "FILTER_LEFT": {"siid": 10, "piid": 2},
    "MOP_PAD_TIME_LEFT": {"siid": 11, "piid": 1},
    "MOP_PAD_LEFT": {"siid": 11, "piid": 2},
}

_S20_PLUS_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 6},
    "RESUME": {"siid": 6, "aiid": 1},
    "CHARGE": {"siid": 3, "aiid": 1},
    "LOCATE": {"siid": 6, "aiid": 6},
    "START_CUSTOM": {"siid": 6, "aiid": 7},
    "RESET_MAIN_BRUSH": {"siid": 8, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 9, "aiid": 1},
    "RESET_FILTER": {"siid": 10, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 11, "aiid": 1},
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
    "SCHEDULE": {"siid": 2, "piid": 19},
    "CARPET_BOOST": {"siid": 2, "piid": 20},
    "RESUME_CLEANING": {"siid": 2, "piid": 23},
    "RELOCATION_STATUS": {"siid": 2, "piid": 26},
    "AUTO_DUST_COLLECTING": {"siid": 2, "piid": 32},
    "AUTO_EMPTY_FREQUENCY": {"siid": 2, "piid": 33},
    "CLEANING_PROPERTIES": {"siid": 2, "piid": 40},
    "FAULTS": {"siid": 2, "piid": 66},
    "CARPET_CLEANING": {"siid": 2, "piid": 73},
    "BATTERY_LEVEL": {"siid": 3, "piid": 1},
    "CHARGING_STATUS": {"siid": 3, "piid": 2},
    "VOLUME": {"siid": 4, "piid": 2},
    "CHILD_LOCK": {"siid": 5, "piid": 1},
    "MOP_PAD_LEFT": {"siid": 9, "piid": 1},
    "MOP_PAD_TIME_LEFT": {"siid": 9, "piid": 2},
    "DND": {"siid": 11, "piid": 1},
    "MAIN_BRUSH_LEFT": {"siid": 12, "piid": 1},
    "MAIN_BRUSH_TIME_LEFT": {"siid": 12, "piid": 2},
    "SIDE_BRUSH_LEFT": {"siid": 13, "piid": 1},
    "SIDE_BRUSH_TIME_LEFT": {"siid": 13, "piid": 2},
    "FILTER_LEFT": {"siid": 14, "piid": 1},
    "FILTER_TIME_LEFT": {"siid": 14, "piid": 2},
    "DETERGENT_LEFT": {"siid": 18, "piid": 1},
}

_X20_MAX_ACTIONS: Final[dict[str, dict[str, int]]] = {
    "START": {"siid": 2, "aiid": 1},
    "STOP": {"siid": 2, "aiid": 2},
    "PAUSE": {"siid": 2, "aiid": 7},
    "RESUME": {"siid": 2, "aiid": 8},
    "START_CUSTOM": {"siid": 2, "aiid": 9},
    "START_AUTO_EMPTY": {"siid": 2, "aiid": 18},
    "CHARGE": {"siid": 3, "aiid": 1},
    "LOCATE": {"siid": 6, "aiid": 1},
    "RESET_MOP_PAD": {"siid": 9, "aiid": 1},
    "RESET_MAIN_BRUSH": {"siid": 12, "aiid": 1},
    "RESET_SIDE_BRUSH": {"siid": 13, "aiid": 1},
    "RESET_FILTER": {"siid": 14, "aiid": 1},
    "RESET_DETERGENT": {"siid": 18, "aiid": 1},
}

# ov31gl uses the X20 Max siid/piid table. Copies are isolated so one model cannot mutate the other.
_ROBOT_VACUUM_5_PROPERTIES: Final[dict[str, dict[str, int]]] = {
    **{name: dict(address) for name, address in _X20_MAX_PROPERTIES.items()},
    "TOTAL_CLEANED_AREA": {"siid": 2, "piid": 85},
    "CLEANING_COUNT": {"siid": 2, "piid": 86},
    "TOTAL_CLEANING_TIME": {"siid": 2, "piid": 87},
    "DETERGENT_TIME_LEFT": {"siid": 18, "piid": 4},
}
_ROBOT_VACUUM_5_ACTIONS: Final[dict[str, dict[str, int]]] = {
    name: dict(address) for name, address in _X20_MAX_ACTIONS.items()
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
        if property_name == "CHARGING_STATUS" and number == _NOT_CHARGEABLE:
            return _NOT_CHARGING
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
        if charging_code == _CHARGING:
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

    def apply_capabilities(self, capability: object) -> None:
        """Replace catalog flags with the flags this model's map can justify."""
        names = _flag_names(self.property_overrides, self.action_overrides)
        state = vars(capability)
        for name, value in list(state.items()):
            if name.startswith("_") or not isinstance(value, bool):
                continue
            state[name] = name in names
        state["_custom_cleaning_mode"] = False
        state["_walls"] = False
        _assign_robot_type(capability, names)
        _rebuild_capability_list(capability)


def resolve_family(model: str) -> XiaomiModel | None:
    """Return the Xiaomi codec for a supported model, otherwise None."""
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
# Old remote code. The shell rewrites it to the current remote state; 23 would become washing-paused.
_LEGACY_REMOTE_CONTROL: Final = 19
# 22-24 stay on Dreame states below 19 so the legacy state remap does not rewrite them.
_ROBOT_VACUUM_5_STATES: Final[dict[int, int]] = {
    **_X20_MAX_STATES,
    int(_X20MaxState.REMOTE): _LEGACY_REMOTE_CONTROL,
    int(_RobotVacuum5State.STATION_ASSISTING): int(_StoredState.WASHING),
    int(_RobotVacuum5State.STATION_ASSISTED): int(_StoredState.CHARGING_COMPLETED),
    int(_RobotVacuum5State.RETURNING_DURING_ASSIST): int(_StoredState.RETURNING),
}
_ROBOT_VACUUM_5_TASKS: Final[dict[int, int]] = {
    **_X20_MAX_TASKS,
    int(_RobotVacuum5Task.APPOINTMENT): int(_StoredTask.AUTO_CLEANING),
    int(_RobotVacuum5Task.LINKAGE): int(_StoredTask.AUTO_CLEANING),
    int(_RobotVacuum5Task.FAST_MAPPING): int(_StoredTask.FAST_MAPPING),
    int(_RobotVacuum5Task.AI_HOSTING): int(_StoredTask.AUTO_CLEANING),
}

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
    MODEL_ROBOT_VACUUM_5: XiaomiModel(
        model=MODEL_ROBOT_VACUUM_5,
        property_overrides=_ROBOT_VACUUM_5_PROPERTIES,
        action_overrides=_ROBOT_VACUUM_5_ACTIONS,
        state_by_wire=_ROBOT_VACUUM_5_STATES,
        task_by_wire=_ROBOT_VACUUM_5_TASKS,
    ),
}


def _flag_names(
    properties: Mapping[str, Mapping[str, int]],
    actions: Mapping[str, Mapping[str, int]],
) -> frozenset[str]:
    """Return feature flags whose property or action is actually mapped."""
    props = frozenset(properties)
    acts = frozenset(actions)
    names = {"mijia"}
    if "SENSOR_DIRTY_LEFT" not in props:
        names.add("disable_sensor_cleaning")
    if "DND" in props or "DND_TASK" in props:
        names.add("dnd")
    if "DND_TASK" in props:
        names.add("dnd_task")
    if "CARPET_RECOGNITION" in props:
        names.add("carpet_recognition")
    if "SELF_WASH_BASE_STATUS" in props or "START_WASHING" in acts:
        names.add("self_wash_base")
    if "WASHBOARD_CLEANING_STATUS" in props:
        names.add("station_cleaning")
    if "START_AUTO_EMPTY" in acts:
        names.add("auto_empty_base")
        names.add("auto_emptying")
    if "DETERGENT_LEFT" in props and "RESET_DETERGENT" in acts:
        names.add("detergent")
    if "DRAINAGE_STATUS" in props:
        names.add("drainage")
    if "OFF_PEAK_CHARGING" in props:
        names.add("off_peak_charging")
    if "WIFI_MAP" in props:
        names.add("wifi_map")
    if "MAP_BACKUP_STATUS" in props or "BACKUP_MAP" in acts:
        names.add("backup_map")
    if "MAP_DATA" in props or "MAP_SAVING" in props:
        names.add("lidar_navigation")
    if "MULTI_FLOOR_MAP" in props:
        names.add("multi_floor_map")
    return frozenset(names)


def _assign_robot_type(capability: object, names: frozenset[str]) -> None:
    current = vars(capability).get("robot_type")
    if not isinstance(current, IntEnum):
        return
    kind = type(current)
    if "self_wash_base" in names and "mop_pad_lifting" in names:
        chosen = kind["SWEEPING_AND_MOPPING"]
    elif "self_wash_base" in names:
        chosen = kind["MOPPING"]
    else:
        # Lidar hardware. Map features stay off until a map property is mapped.
        chosen = kind["LIDAR"]
    vars(capability)["robot_type"] = chosen


def _rebuild_capability_list(capability: object) -> None:
    state = vars(capability)
    names = [
        key
        for key, value in state.items()
        if not callable(value) and not key.startswith("_") and value is True
    ]
    if capability.custom_cleaning_mode:
        names.append("custom_cleaning_mode")
    if capability.cruising:
        names.append("cruising")
    if capability.map:
        names.append("map")
    if capability.walls:
        names.append("walls")
    state["list"] = names
