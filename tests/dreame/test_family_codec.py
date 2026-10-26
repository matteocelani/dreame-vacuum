"""Codec application onto a Dreame device without opening a socket."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.family_codec import apply_family
from custom_components.dreame_vacuum.dreame.types import (
    DID,
    DreameVacuumAction,
    DreameVacuumProperty,
    DreameVacuumPropertyMapping,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.mapping import MODEL_S20_PLUS, MODEL_X20_MAX


class _MapManager:
    def __init__(self) -> None:
        self.action_mapping = None


class _Protocol:
    def __init__(self) -> None:
        self.property_transport = "unset"


class _Device:
    def __init__(self, host: str = "", token: str = "") -> None:
        self.property_mapping = None
        self.action_mapping = None
        self._property_codec = None
        self._map_manager = _MapManager()
        self._protocol = _Protocol()
        self.host = host
        self.token = token


class _Transport:
    def __init__(self, answers: bool) -> None:
        self.answers = answers
        self.probed = False

    def probe(self) -> bool:
        self.probed = True
        return self.answers


class _Family:
    def __init__(self, transport: _Transport | None) -> None:
        self.model = MODEL_S20_PLUS
        self.property_overrides = {"VOLUME": {"siid": 4, "piid": 2}}
        self.action_overrides = {"LOCATE": {}}
        self.transport = transport
        self.built = False

    def build_property_transport(self, host: str, token: str) -> _Transport | None:
        self.built = True
        assert host == "127.0.0.1"
        assert token == "00" * 16
        return self.transport


def test_apply_family_merges_x20_max_and_drops_colliding_properties():
    family = resolve_family(MODEL_X20_MAX)
    assert family is not None
    device = _Device()
    apply_family(device, family)
    assert device._property_codec is family
    assert device._map_manager.action_mapping is device.action_mapping
    assert device.property_mapping[DreameVacuumProperty.STATE] == {"siid": 2, "piid": 2}
    assert device.property_mapping[DreameVacuumProperty.ERROR] == {"siid": 2, "piid": 3}
    assert device.action_mapping[DreameVacuumAction.REQUEST_MAP] == {
        "siid": 10,
        "aiid": 7,
    }
    assert "siid" not in device.action_mapping[DreameVacuumAction.WIFI_MAP]
    assert device._protocol.property_transport is None
    pairs: dict[tuple[int, int], list[str]] = {}
    for prop, mapping in device.property_mapping.items():
        pair = (mapping["siid"], mapping["piid"])
        pairs.setdefault(pair, []).append(prop.name)
    override_names = set(family.property_overrides)
    shared_with_override = [
        set(names)
        for names in pairs.values()
        if len(names) > 1 and set(names) & override_names
    ]
    assert shared_with_override == [{"MAP_DATA", "OBJECT_NAME"}]
    assert all(names <= override_names for names in shared_with_override)
    override_pairs = {
        (item["siid"], item["piid"])
        for item in family.property_overrides.values()
        if "siid" in item
    }
    dropped = [
        prop.name
        for prop, mapping in DreameVacuumPropertyMapping.items()
        if prop.name not in family.property_overrides
        and (mapping.get("siid"), mapping.get("piid")) in override_pairs
        and prop not in device.property_mapping
    ]
    assert dropped
    assert DID(2, 2, device.property_mapping) is DreameVacuumProperty.STATE
    assert DID(2, 1, {DreameVacuumProperty.VOLUME: {"siid": 4, "piid": 2}}) is None


def test_apply_family_disables_s20_plus_map_requests():
    family = resolve_family(MODEL_S20_PLUS)
    assert family is not None
    device = _Device()
    apply_family(device, family)
    assert device.action_mapping[DreameVacuumAction.REQUEST_MAP] == {}
    assert "STATE" not in family.property_overrides
    assert DID(2, 1, device.property_mapping) is DreameVacuumProperty.STATE


def test_apply_family_attaches_transport_only_when_the_probe_answers():
    answering = _Transport(True)
    family = _Family(answering)
    device = _Device("127.0.0.1", "00" * 16)
    apply_family(device, family)
    assert answering.probed is True
    assert device._protocol.property_transport is answering
    silent = _Transport(False)
    apply_family(_Device("127.0.0.1", "00" * 16), _Family(silent))
    assert silent.probed is True
    quiet = _Family(None)
    untouched = _Device("127.0.0.1", "00" * 16)
    apply_family(untouched, quiet)
    assert quiet.built is True
    assert untouched._protocol.property_transport is None
    skipped = _Family(_Transport(True))
    apply_family(_Device(), skipped)
    assert skipped.built is False
