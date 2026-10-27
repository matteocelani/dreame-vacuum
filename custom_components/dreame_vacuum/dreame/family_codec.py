"""Apply a Xiaomi codec to a Dreame vacuum device."""

from __future__ import annotations

import logging

from .types import DreameVacuumAction, DreameVacuumProperty

_LOGGER = logging.getLogger(__name__)


def apply_family(device: object, family: object) -> None:
    """Install explicit maps, then keep a local transport so a later poll can retry."""
    property_overrides = family.property_overrides
    action_overrides = family.action_overrides
    device.property_mapping = _explicit_property_map(property_overrides)
    device.action_mapping = _explicit_action_map(action_overrides)
    device._property_codec = family
    if device._map_manager is not None:
        device._map_manager.action_mapping = device.action_mapping
    transport = _property_transport(device, family)
    if transport is None:
        device._protocol.property_transport = None
    else:
        # Keep the transport when the robot is offline so a later poll can retry.
        if not transport.probe():
            _LOGGER.warning(
                "Local miIO probe failed for model %s; property calls will retry",
                family.model,
            )
        device._protocol.property_transport = transport
    _LOGGER.info("Applied family codec for model %s", family.model)


def _property_transport(device: object, family: object) -> object | None:
    host = device.host
    token = device.token
    if not isinstance(host, str) or not host or not isinstance(token, str) or not token:
        return None
    return family.build_property_transport(host, token)


def _explicit_property_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumProperty, dict[str, int]]:
    # Dreame defaults are a different product. An omitted Xiaomi property is not read.
    merged: dict[DreameVacuumProperty, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "piid" not in mapping:
            continue
        merged[DreameVacuumProperty[name]] = mapping
    return merged


def _explicit_action_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumAction, dict[str, int]]:
    merged: dict[DreameVacuumAction, dict[str, int]] = {}
    for name, mapping in overrides.items():
        if "siid" not in mapping or "aiid" not in mapping:
            continue
        merged[DreameVacuumAction[name]] = mapping
    return merged
