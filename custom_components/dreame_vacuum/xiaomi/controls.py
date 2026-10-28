"""Declarative Xiaomi controls shared by every model record."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol, runtime_checkable

from .exceptions import XiaomiControlException

_MIOT_BATCH: Final = 10


@runtime_checkable
class _ControlStore(Protocol):
    """A device that keeps the last polled control values."""

    _xiaomi_values: dict[str, object]


class ControlDomain(StrEnum):
    """Home Assistant domain a Xiaomi control renders as."""

    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    SWITCH = "switch"
    NUMBER = "number"
    SELECT = "select"
    BUTTON = "button"


class ValueKind(StrEnum):
    """Wire value a control reads or writes."""

    BOOL = "bool"
    INT = "int"
    ENUM = "enum"
    STRING = "string"


@dataclass(frozen=True, slots=True)
class XiaomiControl:
    """One user-facing MIoT property or parameter-free action."""

    key: str
    domain: ControlDomain
    siid: int | None = None
    piid: int | None = None
    aiid: int | None = None
    property_name: str | None = None
    writable: bool = False
    value_kind: ValueKind = ValueKind.INT
    minimum: int | None = None
    maximum: int | None = None
    step: int = 1
    options: tuple[tuple[int, str], ...] = ()
    diagnostic: bool = False
    unit: str | None = None


def boolean_switch(key: str, siid: int, piid: int) -> XiaomiControl:
    """A writable boolean setting."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SWITCH,
        siid=siid,
        piid=piid,
        writable=True,
        value_kind=ValueKind.BOOL,
    )


def enum_select(
    key: str,
    siid: int,
    piid: int,
    options: tuple[tuple[int, str], ...],
) -> XiaomiControl:
    """A writable value-list setting."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SELECT,
        siid=siid,
        piid=piid,
        writable=True,
        value_kind=ValueKind.ENUM,
        options=options,
    )


def mapped_select(
    key: str,
    property_name: str,
    options: tuple[tuple[int, str], ...],
) -> XiaomiControl:
    """A value-list select for a property already in the model map."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SELECT,
        property_name=property_name,
        writable=True,
        value_kind=ValueKind.ENUM,
        options=options,
    )


def measurement(
    key: str,
    siid: int,
    piid: int,
    minimum: int,
    maximum: int,
    unit: str | None = None,
) -> XiaomiControl:
    """A read-only numeric sensor."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SENSOR,
        siid=siid,
        piid=piid,
        value_kind=ValueKind.INT,
        minimum=minimum,
        maximum=maximum,
        diagnostic=True,
        unit=unit,
    )


def enum_sensor(
    key: str,
    siid: int,
    piid: int,
    options: tuple[tuple[int, str], ...],
) -> XiaomiControl:
    """A read-only value-list sensor."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SENSOR,
        siid=siid,
        piid=piid,
        value_kind=ValueKind.ENUM,
        options=options,
        diagnostic=True,
    )


def text_sensor(key: str, siid: int, piid: int) -> XiaomiControl:
    """A read-only string the app shows as text."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.SENSOR,
        siid=siid,
        piid=piid,
        value_kind=ValueKind.STRING,
        diagnostic=True,
    )


def binary_reading(key: str, siid: int, piid: int) -> XiaomiControl:
    """A read-only boolean."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.BINARY_SENSOR,
        siid=siid,
        piid=piid,
        value_kind=ValueKind.BOOL,
        diagnostic=True,
    )


def number_control(
    key: str,
    siid: int,
    piid: int,
    minimum: int,
    maximum: int,
    step: int = 1,
) -> XiaomiControl:
    """A writable integer range."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.NUMBER,
        siid=siid,
        piid=piid,
        writable=True,
        value_kind=ValueKind.INT,
        minimum=minimum,
        maximum=maximum,
        step=step,
    )


def action_button(key: str, siid: int, aiid: int) -> XiaomiControl:
    """An action the spec invokes with an empty parameter list."""
    return XiaomiControl(
        key=key,
        domain=ControlDomain.BUTTON,
        siid=siid,
        aiid=aiid,
        writable=True,
    )


def read_control(device: object, control: XiaomiControl) -> object:
    """Return the last polled value for a direct MIoT control."""
    if control.piid is None:
        return None
    store = _stored_values(device)
    if store is None:
        return None
    return store.get(control.key)


def write_control(device: object, control: XiaomiControl, value: object) -> None:
    """Send one control value. Property-map controls are written by the shell."""
    if control.siid is None or control.piid is None:
        raise XiaomiControlException(control.key)
    result = device._protocol.set_property(control.siid, control.piid, value)
    if not _accepted(result):
        raise XiaomiControlException(control.key)
    store = _stored_values(device)
    if store is not None:
        store[control.key] = value


def invoke_control(device: object, control: XiaomiControl) -> None:
    """Invoke a parameter-free action."""
    if control.siid is None or control.aiid is None:
        raise XiaomiControlException(control.key)
    result = device._protocol.action(control.siid, control.aiid, [])
    if not isinstance(result, dict) or result.get("code") != 0:
        raise XiaomiControlException(control.key)


def refresh_controls(device: object, controls: tuple[XiaomiControl, ...]) -> bool:
    """Poll direct control properties in MIoT-sized batches."""
    pending = [
        control
        for control in controls
        if control.siid is not None and control.piid is not None
    ]
    if not pending:
        return False
    store = _stored_values(device)
    if store is None:
        return False
    changed = False
    for start in range(0, len(pending), _MIOT_BATCH):
        batch = pending[start : start + _MIOT_BATCH]
        items = [
            {"did": control.key, "siid": control.siid, "piid": control.piid}
            for control in batch
        ]
        result = device._protocol.get_properties(items)
        if not isinstance(result, list):
            raise XiaomiControlException("refresh")
        changed = _store_batch(store, batch, result) or changed
    return changed


def _stored_values(device: object) -> dict[str, object] | None:
    if not isinstance(device, _ControlStore):
        return None
    values = device._xiaomi_values
    if not isinstance(values, dict):
        return None
    return values


def _accepted(result: object) -> bool:
    if not isinstance(result, list) or not result:
        return False
    first = result[0]
    return isinstance(first, dict) and first.get("code") == 0


def _store_batch(
    store: dict[str, object],
    batch: list[XiaomiControl],
    result: list[object],
) -> bool:
    changed = False
    for item in result:
        if not isinstance(item, dict) or item.get("code") != 0 or "value" not in item:
            continue
        siid = item.get("siid")
        piid = item.get("piid")
        for control in batch:
            if control.siid == siid and control.piid == piid:
                value = item.get("value")
                if store.get(control.key) != value:
                    store[control.key] = value
                    changed = True
    return changed
