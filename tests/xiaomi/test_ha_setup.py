"""Home Assistant setup against the loopback miIO device for both models."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

from custom_components.dreame_vacuum.const import (
    CONF_ACCOUNT_TYPE,
    CONF_MAC,
    CONF_NOTIFY,
    CONF_PREFER_CLOUD,
    CONF_VERSION,
    DOMAIN,
)
from custom_components.dreame_vacuum.xiaomi.mapping import MODEL_S20_PLUS, MODEL_X20_MAX
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from tests.xiaomi.helpers import FakeMiio, release_device

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.core import HomeAssistant

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_FORBIDDEN = {(7, 2), (6, 3), (15, 1), (19, 1), (20, 1), (10, 7), (18, 1)}

pytestmark = [
    pytest.mark.ha,
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


@pytest.fixture
def integration_package() -> object:
    """Load the real integration package over the device-core import stub."""
    dreame_name = "custom_components.dreame_vacuum.dreame"
    dreame = sys.modules.get(dreame_name)
    if dreame is not None and not hasattr(dreame, "VERSION"):
        init = (
            Path(__file__).resolve().parents[2]
            / "custom_components"
            / "dreame_vacuum"
            / "dreame"
            / "__init__.py"
        )
        executed = compile(init.read_text(encoding="utf-8"), str(init), "exec")
        exec(executed, dreame.__dict__)
    package = "custom_components.dreame_vacuum"
    module = sys.modules.get(package)
    if module is None or not hasattr(module, "async_setup_entry"):
        sys.modules.pop(package, None)
        module = importlib.import_module(package)
    return module


async def test_setup_creates_vacuum_and_safe_commands_for_both_models(
    hass: HomeAssistant,
    socket_enabled: None,
    enable_custom_integrations: None,
    integration_package: object,
) -> None:
    """Set up each model, drive the dock cycle, and record every action."""
    del integration_package
    from custom_components.dreame_vacuum.dreame import VERSION
    from custom_components.dreame_vacuum.xiaomi import resolve_family

    for model, name in ((MODEL_S20_PLUS, "S20 Sim"), (MODEL_X20_MAX, "X20 Sim")):
        family = resolve_family(model)
        assert family is not None
        actions = family.action_overrides
        with FakeMiio(model) as fake:
            entry = MockConfigEntry(
                domain=DOMAIN,
                unique_id=name,
                data={
                    CONF_NAME: name,
                    CONF_HOST: "127.0.0.1",
                    CONF_TOKEN: _TOKEN,
                    CONF_MAC: _MAC,
                    CONF_ACCOUNT_TYPE: "mi",
                },
                options={
                    CONF_PREFER_CLOUD: False,
                    CONF_NOTIFY: False,
                    CONF_VERSION: VERSION,
                },
            )
            entry.add_to_hass(hass)
            assert await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            device = hass.data[DOMAIN][entry.entry_id].device
            try:
                vacuum = _vacuum(hass)
                assert vacuum.state == "docked"
                assert not _unsafe_entities(hass)
                await _cycle(hass, vacuum.entity_id)
                await _refresh(hass, entry.entry_id)
                assert _vacuum(hass).state == "cleaning"
                await hass.services.async_call(
                    "vacuum",
                    "pause",
                    {"entity_id": vacuum.entity_id},
                    blocking=True,
                )
                await _refresh(hass, entry.entry_id)
                assert _vacuum(hass).state == "paused"
                await hass.services.async_call(
                    "vacuum",
                    "start",
                    {"entity_id": vacuum.entity_id},
                    blocking=True,
                )
                await hass.services.async_call(
                    "vacuum",
                    "return_to_base",
                    {"entity_id": vacuum.entity_id},
                    blocking=True,
                )
                await _refresh(hass, entry.entry_id)
                assert _vacuum(hass).state == "docked"
            finally:
                assert await hass.config_entries.async_unload(entry.entry_id)
                await hass.async_block_till_done()
                release_device(device)
        assert fake.actions == [
            (actions["START"]["siid"], actions["START"]["aiid"]),
            (actions["PAUSE"]["siid"], actions["PAUSE"]["aiid"]),
            (actions["RESUME"]["siid"], actions["RESUME"]["aiid"]),
            (actions["CHARGE"]["siid"], actions["CHARGE"]["aiid"]),
        ]
        assert not set(fake.actions) & _FORBIDDEN


def _vacuum(hass: HomeAssistant):
    states = [state for state in hass.states.async_all() if state.domain == "vacuum"]
    assert len(states) == 1
    return states[0]


def _unsafe_entities(hass: HomeAssistant) -> list[str]:
    blocked = (
        "off_peak",
        "silver_ion",
        "backup_saved_map",
        "play_sound",
        "start_fast_mapping",
        "start_mapping",
    )
    return [
        state.entity_id
        for state in hass.states.async_all()
        if state.domain == "time" or any(name in state.entity_id for name in blocked)
    ]


async def _cycle(hass: HomeAssistant, entity_id: str) -> None:
    await hass.services.async_call(
        "vacuum",
        "start",
        {"entity_id": entity_id},
        blocking=True,
    )


async def _refresh(hass: HomeAssistant, entry_id: str) -> None:
    coordinator = hass.data[DOMAIN][entry_id]
    await hass.async_add_executor_job(coordinator.device._request_properties)
    coordinator.async_set_updated_data()
    await hass.async_block_till_done()
