"""Drive both models through a loopback miIO device and record every action."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.device import DreameVacuumDevice
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumProperty,
    DreameVacuumState,
)
from custom_components.dreame_vacuum.xiaomi import resolve_family
from custom_components.dreame_vacuum.xiaomi.mapping import (
    MODEL_ROBOT_VACUUM_5,
    MODEL_S20_PLUS,
    MODEL_S40,
    MODEL_S40_PRO,
    MODEL_X20_MAX,
)
import pytest
from tests.xiaomi.helpers import FakeMiio, release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"
_FORBIDDEN = {(7, 2), (6, 3), (15, 1), (19, 1), (20, 1), (10, 7), (18, 1)}

pytestmark = [
    pytest.mark.enable_socket,
    pytest.mark.allow_hosts(["127.0.0.1"]),
]


def test_loopback_device_start_pause_resume_and_dock_send_only_mapped_actions(
    socket_enabled: None,
) -> None:
    for model in (
        MODEL_S20_PLUS,
        MODEL_X20_MAX,
        MODEL_ROBOT_VACUUM_5,
        MODEL_S40_PRO,
        MODEL_S40,
    ):
        family = resolve_family(model)
        assert family is not None
        actions = family.action_overrides
        with FakeMiio(model) as fake:
            device = DreameVacuumDevice(
                "Sim",
                "127.0.0.1",
                _TOKEN,
                _MAC,
                account_type="mi",
                family_resolver=resolve_family,
            )
            device.connect_device()
            try:
                assert device.info is not None
                assert device.info.model == model
                assert int(device.status.state) == int(DreameVacuumState.CHARGING)
                device.start()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.SWEEPING)
                device.pause()
                device._request_properties()
                assert int(device.status.state) == int(DreameVacuumState.PAUSED)
                device.start()
                device.return_to_base()
            finally:
                release_device(device)
        assert fake.actions == [
            (actions["START"]["siid"], actions["START"]["aiid"]),
            (actions["PAUSE"]["siid"], actions["PAUSE"]["aiid"]),
            (actions["RESUME"]["siid"], actions["RESUME"]["aiid"]),
            (actions["CHARGE"]["siid"], actions["CHARGE"]["aiid"]),
        ]
        assert not set(fake.actions) & _FORBIDDEN
        assert DreameVacuumProperty.STATUS not in device.property_mapping
        assert (5, 2) not in {
            (item["siid"], item["piid"]) for item in device.property_mapping.values()
        }
