"""Xiaomi X20 Max model record composed from the station profile."""

from __future__ import annotations

from typing import Final

from .model import MODEL_X20_MAX, XiaomiModel
from .profile import (
    STATION_ACTIONS,
    STATION_PROPERTIES,
    STATION_STATES,
    STATION_TASKS,
    compose_addresses,
    compose_codes,
)

X20_MAX: Final = XiaomiModel(
    model=MODEL_X20_MAX,
    property_overrides=compose_addresses(STATION_PROPERTIES),
    action_overrides=compose_addresses(STATION_ACTIONS),
    state_by_wire=compose_codes(STATION_STATES),
    task_by_wire=compose_codes(STATION_TASKS),
)
