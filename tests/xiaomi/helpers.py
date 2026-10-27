"""In-process miIO device for Xiaomi tests. No network beyond 127.0.0.1."""

from __future__ import annotations

import hashlib
import json
import socket
import struct
import threading
from typing import Final

from Crypto.Cipher import AES
from custom_components.dreame_vacuum.xiaomi import resolve_family


def traffic_outside_map(
    writes: list[tuple[int, int, object]],
    actions: list[tuple[int, int]],
    action_inputs: list[object],
    properties: set[tuple[int, int]],
    action_addresses: set[tuple[int, int]],
) -> tuple[set[tuple[int, int]], set[tuple[int, int]], list[object]]:
    """Return writes, actions, and payloads that leave the model map."""
    write_pairs = {(siid, piid) for siid, piid, _value in writes}
    unexpected = [payload for payload in action_inputs if payload not in ([], None)]
    return (write_pairs - properties, set(actions) - action_addresses, unexpected)


def release_device(device: object) -> None:
    """Stop device timers and wait until their threads have exited."""
    disconnect = getattr(device, "disconnect", None)
    if disconnect is not None:
        disconnect()
    for name in ("_update_timer", "_keep_alive_timer", "_callback_timer"):
        timer = getattr(device, name, None)
        thread = getattr(timer, "_thread", None) if timer is not None else None
        if thread is not None:
            thread.join(timeout=2)


def _plain(payload: bytes) -> bytes:
    pad_length = payload[-1]
    if (
        1 <= pad_length <= 16
        and payload[-pad_length:] == bytes([pad_length]) * pad_length
    ):
        payload = payload[:-pad_length]
    return payload.rstrip(b"\x00")


_PORT: Final = 54321
_TOKEN: Final = "00" * 16
_HEADER: Final = 32


class FakeMiio:
    """Answer miIO handshake, info, properties, and actions for one model."""

    def __init__(self, model: str, token: str = _TOKEN) -> None:
        self.model = model
        self.token = bytes.fromhex(token)
        self.actions: list[tuple[int, int]] = []
        self.action_inputs: list[object] = []
        self.writes: list[tuple[int, int, object]] = []
        self._family = resolve_family(model)
        if self._family is None:
            raise RuntimeError(model)
        self._values = self._initial_values()
        self._stamp = 100
        self._device_id = 7
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        key = hashlib.md5(self.token).digest()
        self._key = key
        self._iv = hashlib.md5(key + self.token).digest()

    def __enter__(self) -> FakeMiio:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start(self) -> None:
        """Bind the miIO port and answer in a background thread."""
        datagram = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        datagram.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        datagram.bind(("127.0.0.1", _PORT))
        datagram.settimeout(0.2)
        self._socket = datagram
        self._running = True
        self._thread = threading.Thread(target=self._serve, name="fake-miio")
        self._thread.start()

    def close(self) -> None:
        """Stop the background thread and release the port."""
        self._running = False
        thread = self._thread
        if thread is not None:
            thread.join(timeout=2)
        datagram = self._socket
        if datagram is not None:
            datagram.close()
        self._socket = None

    def _initial_values(self) -> dict[tuple[int, int], object]:
        values: dict[tuple[int, int], object] = {}
        for mapping in self._family.property_overrides.values():
            values[(mapping["siid"], mapping["piid"])] = 0
        state = self._family.property_overrides["STATE"]
        charging = self._family.property_overrides["CHARGING_STATUS"]
        battery = self._family.property_overrides["BATTERY_LEVEL"]
        values[(state["siid"], state["piid"])] = 2
        values[(charging["siid"], charging["piid"])] = 1
        values[(battery["siid"], battery["piid"])] = 90
        return values

    def _state_pair(self) -> tuple[int, int]:
        mapping = self._family.property_overrides["STATE"]
        return mapping["siid"], mapping["piid"]

    def _set_state(self, wire: int) -> None:
        self._values[self._state_pair()] = wire

    def _charging_pair(self) -> tuple[int, int]:
        mapping = self._family.property_overrides["CHARGING_STATUS"]
        return mapping["siid"], mapping["piid"]

    def _set_charging(self, wire: int) -> None:
        self._values[self._charging_pair()] = wire

    def set_value(self, siid: int, piid: int, value: object) -> None:
        """Store one property the next read will return."""
        self._values[(siid, piid)] = value

    def _serve(self) -> None:
        datagram = self._socket
        if datagram is None:
            return
        while self._running:
            try:
                packet, address = datagram.recvfrom(4096)
            except TimeoutError:
                continue
            except OSError:
                return
            reply = self._reply(packet)
            if reply is not None and self._running:
                datagram.sendto(reply, address)

    def _reply(self, packet: bytes) -> bytes | None:
        if len(packet) < 16:
            return None
        if struct.unpack(">H", packet[2:4])[0] == _HEADER or len(packet) == _HEADER:
            self._stamp += 1
            reply = bytearray(32)
            struct.pack_into(">HH", reply, 0, 0x2131, 32)
            struct.pack_into(">I", reply, 8, self._device_id)
            struct.pack_into(">I", reply, 12, self._stamp)
            return bytes(reply)
        if len(packet) <= _HEADER:
            return None
        decrypted = self._decrypt(packet[_HEADER:])
        if decrypted is None:
            return None
        try:
            request = json.loads(_plain(decrypted))
        except json.JSONDecodeError:
            return None
        if not isinstance(request, dict):
            return None
        result = self._dispatch(request.get("method"), request.get("params"))
        if result is None:
            payload = {"id": request.get("id"), "error": {"code": -1}}
        else:
            payload = {"id": request.get("id"), "result": result}
        return self._encrypt(payload)

    def _dispatch(self, method: object, params: object) -> object | None:
        if method == "miIO.info":
            return {
                "model": self.model,
                "fw_ver": "1.0_1",
                "mac": "00:00:00:00:00:00",
                "hw_ver": "Linux",
                "netif": {"localIp": "127.0.0.1"},
            }
        if method == "get_properties" and isinstance(params, list):
            return [self._read(item) for item in params if isinstance(item, dict)]
        if method == "set_properties" and isinstance(params, list):
            return [self._write(item) for item in params if isinstance(item, dict)]
        if method == "action" and isinstance(params, dict):
            return self._action(params)
        return None

    def _read(self, item: dict[str, object]) -> dict[str, object]:
        siid = item.get("siid")
        piid = item.get("piid")
        if not isinstance(siid, int) or not isinstance(piid, int):
            return {"code": -1000, "siid": siid, "piid": piid}
        pair = (siid, piid)
        if pair not in self._values:
            return {
                "did": item.get("did", ""),
                "siid": siid,
                "piid": piid,
                "code": -1000,
            }
        return {
            "did": item.get("did", ""),
            "siid": siid,
            "piid": piid,
            "code": 0,
            "value": self._values[pair],
        }

    def _write(self, item: dict[str, object]) -> dict[str, object]:
        siid = item.get("siid")
        piid = item.get("piid")
        if isinstance(siid, int) and isinstance(piid, int):
            self.writes.append((siid, piid, item.get("value")))
            self._values[(siid, piid)] = item.get("value")
        return {"did": item.get("did", ""), "siid": siid, "piid": piid, "code": 0}

    def _action(self, params: dict[str, object]) -> dict[str, int]:
        siid = params.get("siid")
        aiid = params.get("aiid")
        if not isinstance(siid, int) or not isinstance(aiid, int):
            return {"code": -1}
        self.actions.append((siid, aiid))
        self.action_inputs.append(params.get("in"))
        address = (siid, aiid)
        actions = self._family.action_overrides
        if address == (
            actions["START"]["siid"],
            actions["START"]["aiid"],
        ) or address == (actions["RESUME"]["siid"], actions["RESUME"]["aiid"]):
            self._set_state(4)
            self._set_charging(2)
        elif address == (actions["PAUSE"]["siid"], actions["PAUSE"]["aiid"]):
            self._set_state(5)
            self._set_charging(2)
        elif address == (actions["CHARGE"]["siid"], actions["CHARGE"]["aiid"]):
            self._set_state(2)
            self._set_charging(1)
        return {"code": 0}

    def _decrypt(self, payload: bytes) -> bytes | None:
        if not payload or len(payload) % 16 != 0:
            return None
        return AES.new(self._key, AES.MODE_CBC, self._iv).decrypt(payload)

    def _encrypt(self, payload: object) -> bytes:
        raw = json.dumps(payload).encode() + b"\x00"
        pad_length = 16 - (len(raw) % 16)
        encrypted = AES.new(self._key, AES.MODE_CBC, self._iv).encrypt(
            raw + bytes([pad_length] * pad_length)
        )
        self._stamp += 1
        header = struct.pack(">HH", 0x2131, _HEADER + len(encrypted))
        header += b"\x00\x00\x00\x00"
        header += struct.pack(">II", self._device_id, self._stamp)
        checksum = hashlib.md5(header + self.token + encrypted).digest()
        return header + checksum + encrypted
