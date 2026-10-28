"""Command routing for S20+ and X20 Max stays on the mapped action."""

from __future__ import annotations

from custom_components.dreame_vacuum.dreame.device import (
    DreameVacuumDevice,
    DreameVacuumDeviceInfo,
)
from custom_components.dreame_vacuum.dreame.exceptions import InvalidActionException
from custom_components.dreame_vacuum.dreame.map import DreameMapVacuumMapManager
from custom_components.dreame_vacuum.dreame.types import (
    DreameVacuumAction,
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
from tests.xiaomi.helpers import release_device

_TOKEN = "00" * 16
_MAC = "00:00:00:00:00:00"


def _device(model: str) -> tuple[DreameVacuumDevice, list[tuple[int, int]]]:
    device = DreameVacuumDevice(
        "Sim",
        "127.0.0.1",
        _TOKEN,
        _MAC,
        family_resolver=resolve_family,
    )
    device.host = ""
    device.info = DreameVacuumDeviceInfo(
        {
            "model": model,
            "fw_ver": "1.0_1",
            "mac": _MAC,
            "netif": {"localIp": "127.0.0.1"},
        }
    )
    device._apply_reported_family()
    sent: list[tuple[int, int]] = []

    def action(
        siid: int, aiid: int, parameters: object = None, retry_count: int = 2
    ) -> dict[str, int]:
        del parameters, retry_count
        sent.append((siid, aiid))
        return {"code": 0}

    def set_property(
        siid: int, piid: int, value: object = None, retry_count: int = 2
    ) -> list[dict[str, int]]:
        del siid, piid, value, retry_count
        return [{"code": 0}]

    device._protocol.action = action
    device._protocol.set_property = set_property
    return device, sent


def test_paused_start_uses_continue_sweep_and_skips_unmapped_actions():
    expected = {
        MODEL_S20_PLUS: {
            "resume": (6, 1),
            "start": (2, 1),
            "pause": (2, 6),
            "charge": (3, 1),
        },
        MODEL_X20_MAX: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_ROBOT_VACUUM_5: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S40_PRO: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
        MODEL_S40: {
            "resume": (2, 8),
            "start": (2, 1),
            "pause": (2, 7),
            "charge": (3, 1),
        },
    }
    for model, addresses in expected.items():
        device, sent = _device(model)
        try:
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.PAUSED
            )
            device.start()
            assert sent[-1] == addresses["resume"]
            device.data[DreameVacuumProperty.STATE.value] = int(
                DreameVacuumState.SWEEPING
            )
            device.pause()
            assert sent[-1] == addresses["pause"]
            device.data[DreameVacuumProperty.STATE.value] = int(DreameVacuumState.IDLE)
            device.start()
            assert sent[-1] == addresses["start"]
            device.return_to_base()
            assert sent[-1] == addresses["charge"]
            device.set_volume(40)
            forbidden = {
                device.action_mapping[item]
                for item in (
                    DreameVacuumAction.PLAY_SOUND,
                    DreameVacuumAction.BACKUP_MAP,
                    DreameVacuumAction.REQUEST_MAP,
                    DreameVacuumAction.RESET_SILVER_ION,
                )
                if item in device.action_mapping
            }
            assert not forbidden
            for siid, aiid in sent:
                assert (siid, aiid) in set(addresses.values())
            with pytest.raises(InvalidActionException):
                device.call_action(DreameVacuumAction.PLAY_SOUND)
            assert sent[-1] == addresses["charge"]
            manager = DreameMapVacuumMapManager.__new__(DreameMapVacuumMapManager)
            manager.action_mapping = device.action_mapping
            assert manager._mapped_action(DreameVacuumAction.REQUEST_MAP) is None
            assert manager._mapped_action(DreameVacuumAction.UPDATE_MAP_DATA) is None
            manager.action_mapping = None
            dreame_map = manager._mapped_action(DreameVacuumAction.REQUEST_MAP)
            assert dreame_map is not None
            assert dreame_map["siid"] == 6
        finally:
            release_device(device)


def test_property_reads_stay_inside_the_explicit_map():
    for model in (
        MODEL_S20_PLUS,
        MODEL_X20_MAX,
        MODEL_ROBOT_VACUUM_5,
        MODEL_S40_PRO,
        MODEL_S40,
    ):
        device, _sent = _device(model)
        requested: list[tuple[int, int]] = []

        def get_properties(
            parameters: list[dict[str, int]],
            retry_count: int = 1,
            timeout: object = None,
            requested: list[tuple[int, int]] = requested,
        ) -> list[dict[str, object]]:
            del retry_count, timeout
            requested.extend((item["siid"], item["piid"]) for item in parameters)
            return [
                {
                    "did": item["did"],
                    "siid": item["siid"],
                    "piid": item["piid"],
                    "code": 0,
                    "value": 0,
                }
                for item in parameters
            ]

        device._protocol.get_properties = get_properties
        device._request_properties()
        allowed = {
            (mapping["siid"], mapping["piid"])
            for mapping in device.property_mapping.values()
        }
        controls = {
            (control.siid, control.piid)
            for control in device._property_codec.controls
            if control.siid is not None and control.piid is not None
        }
        assert requested
        assert set(requested) <= allowed | controls
        assert (7, 2) not in requested
        if model in (MODEL_ROBOT_VACUUM_5, MODEL_S40_PRO, MODEL_S40):
            assert (4, 1) in requested
            assert (5, 2) in requested
        if model == MODEL_S40_PRO:
            assert (18, 1) not in requested
            assert (19, 1) not in requested
        if model == MODEL_S40:
            assert (18, 1) in requested
            assert (19, 1) in requested
        if model not in (MODEL_ROBOT_VACUUM_5, MODEL_S40_PRO, MODEL_S40):
            assert controls == set()
            assert (4, 1) not in requested
            assert (5, 2) not in requested
