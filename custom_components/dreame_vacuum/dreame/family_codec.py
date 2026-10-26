"""Apply a Xiaomi codec to a Dreame vacuum device."""

from __future__ import annotations

import logging

from .types import (
    DreameVacuumAction,
    DreameVacuumActionMapping,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
)

_LOGGER = logging.getLogger(__name__)


def apply_family(device: object, family: object) -> None:
    """Install property and action overrides, then attach a local transport if it answers."""
    property_overrides = family.property_overrides
    action_overrides = family.action_overrides
    device.property_mapping = _merge_property_map(property_overrides)
    device.action_mapping = _merge_action_map(action_overrides)
    device._property_codec = family
    if device._map_manager is not None:
        device._map_manager.action_mapping = device.action_mapping
    transport = _property_transport(device, family)
    if transport is not None and transport.probe():
        device._protocol.property_transport = transport
    else:
        device._protocol.property_transport = None
    _LOGGER.info("Applied family codec for model %s", family.model)


def _property_transport(device: object, family: object) -> object | None:
    host = device.host
    token = device.token
    if not isinstance(host, str) or not host or not isinstance(token, str) or not token:
        return None
    return family.build_property_transport(host, token)


def _merge_property_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumProperty, dict[str, int]]:
    merged: dict[DreameVacuumProperty, dict[str, int]] = dict(
        DreameVacuumPropertyMapping
    )
    override_properties: set[DreameVacuumProperty] = set()
    override_pairs: set[tuple[int, int]] = set()
    for name, mapping in overrides.items():
        prop = DreameVacuumProperty[name]
        merged[prop] = mapping
        override_properties.add(prop)
        siid = mapping.get("siid")
        piid = mapping.get("piid")
        if siid is not None and piid is not None:
            override_pairs.add((siid, piid))
    for prop, mapping in list(merged.items()):
        if prop in override_properties:
            continue
        siid = mapping.get("siid")
        piid = mapping.get("piid")
        if siid is not None and piid is not None and (siid, piid) in override_pairs:
            del merged[prop]
    return merged


def _merge_action_map(
    overrides: dict[str, dict[str, int]],
) -> dict[DreameVacuumAction, dict[str, int]]:
    merged: dict[DreameVacuumAction, dict[str, int]] = dict(DreameVacuumActionMapping)
    override_actions: set[DreameVacuumAction] = set()
    override_pairs: set[tuple[int, int]] = set()
    for name, mapping in overrides.items():
        action = DreameVacuumAction[name]
        merged[action] = mapping
        override_actions.add(action)
        siid = mapping.get("siid")
        aiid = mapping.get("aiid")
        if siid is not None and aiid is not None:
            override_pairs.add((siid, aiid))
    for action, mapping in list(merged.items()):
        if action in override_actions:
            continue
        siid = mapping.get("siid")
        aiid = mapping.get("aiid")
        if siid is not None and aiid is not None and (siid, aiid) in override_pairs:
            del merged[action]
    return merged
