"""Shared station address table that X20 Max-like Xiaomi models compose."""

from __future__ import annotations

from collections.abc import Mapping
from enum import IntEnum
from typing import Final


class StoredState(IntEnum):
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


class StoredTask(IntEnum):
    """Dreame task-status codes stored for Xiaomi models."""

    COMPLETED = 0
    AUTO_CLEANING = 1
    ZONE_CLEANING = 2
    SEGMENT_CLEANING = 3
    SPOT_CLEANING = 4
    FAST_MAPPING = 5
    AUTO_CLEANING_PAUSED = 6


class StationWireState(IntEnum):
    """Wire status codes shared by the X20 Max station spec."""

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


class StationWireTask(IntEnum):
    """Wire sweep-type codes shared by the X20 Max station spec."""

    GLOBAL = 1
    ZONE = 2
    AREA = 3
    EDGE = 4
    CUSTOM = 5
    POINT = 6
    CUSTOM_AREA = 7


def wire_map(pairs: tuple[tuple[IntEnum, IntEnum], ...]) -> dict[int, int]:
    """Build a wire-code map from named pairs."""
    return {int(wire): int(stored) for wire, stored in pairs}


def compose_addresses(
    base: Mapping[str, Mapping[str, int]],
    additions: Mapping[str, Mapping[str, int]] | None = None,
) -> dict[str, dict[str, int]]:
    """Copy a shared address table and apply one model's additions."""
    merged = {name: dict(address) for name, address in base.items()}
    if not additions:
        return merged
    for name, address in additions.items():
        merged[name] = dict(address)
    return merged


def compose_codes(
    base: Mapping[int, int],
    overrides: Mapping[int, int] | None = None,
) -> dict[int, int]:
    """Copy a shared wire map and apply one model's overrides."""
    merged = {int(wire): int(stored) for wire, stored in base.items()}
    if overrides:
        for wire, stored in overrides.items():
            merged[int(wire)] = int(stored)
    return merged


STATION_PROPERTIES: Final[dict[str, dict[str, int]]] = {
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

STATION_ACTIONS: Final[dict[str, dict[str, int]]] = {
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

STATION_STATES: Final[dict[int, int]] = wire_map(
    (
        (StationWireState.IDLE, StoredState.IDLE),
        (StationWireState.CHARGING, StoredState.CHARGING),
        (StationWireState.BREAK_CHARGING, StoredState.CHARGING),
        (StationWireState.SWEEPING, StoredState.SWEEPING),
        (StationWireState.PAUSED, StoredState.PAUSED),
        (StationWireState.RETURNING, StoredState.RETURNING),
        (StationWireState.GO_WASH, StoredState.RETURNING_TO_WASH),
        (StationWireState.REMOTE, StoredState.REMOTE_CONTROL),
        (StationWireState.CHARGED, StoredState.CHARGING_COMPLETED),
        (StationWireState.BUILDING, StoredState.BUILDING),
        (StationWireState.UPDATING, StoredState.UPGRADING),
        (StationWireState.MULTI_TASK_STATION, StoredState.STATION_CLEANING),
        (StationWireState.MULTI_TASK_RECHARGE, StoredState.CHARGING),
        (StationWireState.STATION_WORKING, StoredState.STATION_CLEANING),
        (StationWireState.ERROR, StoredState.ERROR),
        (StationWireState.SWEEPING_AND_MOPPING, StoredState.SWEEPING_AND_MOPPING),
        (StationWireState.MOPPING, StoredState.MOPPING),
        (StationWireState.MAPPING_PAUSE, StoredState.PAUSED),
        (StationWireState.GO_CHARGE_BREAK, StoredState.RETURNING),
        (StationWireState.WASH_BREAK, StoredState.RETURNING_TO_WASH),
        (StationWireState.GO_CHARGE_BUILDING, StoredState.BUILDING),
    )
)

STATION_TASKS: Final[dict[int, int]] = wire_map(
    (
        (StationWireTask.GLOBAL, StoredTask.AUTO_CLEANING),
        (StationWireTask.ZONE, StoredTask.ZONE_CLEANING),
        (StationWireTask.AREA, StoredTask.SPOT_CLEANING),
        (StationWireTask.EDGE, StoredTask.ZONE_CLEANING),
        (StationWireTask.CUSTOM, StoredTask.SEGMENT_CLEANING),
        (StationWireTask.POINT, StoredTask.SPOT_CLEANING),
        (StationWireTask.CUSTOM_AREA, StoredTask.ZONE_CLEANING),
    )
)
