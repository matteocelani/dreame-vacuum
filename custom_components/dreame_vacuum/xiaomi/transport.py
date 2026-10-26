"""Local miIO datagram transport for Xiaomi property reads and writes."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import logging
import socket
import struct
import threading
from typing import Final

from Crypto.Cipher import AES

from .exceptions import XiaomiTransportException

_LOGGER = logging.getLogger(__name__)

_MIIO_PORT: Final = 54321
_MIIO_MAGIC: Final = 0x2131
_TIMEOUT_SECONDS: Final = 5.0
_SEND_RETRIES: Final = 2
_TOKEN_HEX_LENGTH: Final = 32
_AES_BLOCK: Final = 16
_HEADER_SIZE: Final = 32
_HEADER_FIELDS: Final = 16
_HANDSHAKE_MIN_LENGTH: Final = 16
_HANDSHAKE_BUFFER: Final = 1024
_RESPONSE_BUFFER: Final = 4096
_MAX_REQUEST_ID: Final = 9999
_HANDSHAKE_PADDING_LENGTH: Final = 28
_HEADER_PADDING: Final = b"\x00\x00\x00\x00"
_HANDSHAKE: Final = bytes.fromhex("21310020") + (b"\xff" * _HANDSHAKE_PADDING_LENGTH)


def _token_bytes(token: str) -> bytes:
    if len(token) != _TOKEN_HEX_LENGTH:
        raise XiaomiTransportException("miIO token is not 32 hexadecimal characters")
    try:
        decoded = bytes.fromhex(token)
    except ValueError:
        raise XiaomiTransportException(
            "miIO token is not 32 hexadecimal characters"
        ) from None
    return decoded


def _pkcs7_pad(payload: bytes) -> bytes:
    pad_length = _AES_BLOCK - (len(payload) % _AES_BLOCK)
    return payload + bytes([pad_length] * pad_length)


def _pkcs7_unpad(payload: bytes) -> bytes | None:
    pad_length = payload[-1]
    if pad_length < 1 or pad_length > _AES_BLOCK:
        return None
    if payload[-pad_length:] != bytes([pad_length] * pad_length):
        return None
    return payload[:-pad_length]


def _aes_encrypt(payload: bytes, key: bytes, iv: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(_pkcs7_pad(payload))


def _aes_decrypt(payload: bytes, key: bytes, iv: bytes) -> bytes | None:
    if not payload or len(payload) % _AES_BLOCK != 0:
        return None
    return _pkcs7_unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(payload))


class MiioPropertyTransport:
    """Sync miIO client for property reads and writes on the local network."""

    def __init__(
        self,
        host: str,
        token: str,
        socket_factory: Callable[[], socket.socket] | None = None,
        timeout: float = _TIMEOUT_SECONDS,
    ) -> None:
        self._host = host
        self._token = _token_bytes(token)
        self._socket_factory = socket_factory
        self._timeout = timeout
        self._discovered = False
        self._device_id = 0
        self._stamp = 0
        self._request_id = 0
        self._lock = threading.Lock()
        self._key = hashlib.md5(self._token).digest()
        self._iv = hashlib.md5(self._key + self._token).digest()

    def __repr__(self) -> str:
        return "MiioPropertyTransport(token_omitted=True)"

    def probe(self) -> bool:
        """Return whether the robot answers a miIO handshake."""
        datagram = self._open()
        try:
            datagram.sendto(_HANDSHAKE, (self._host, _MIIO_PORT))
            data, _address = datagram.recvfrom(_HANDSHAKE_BUFFER)
        except OSError:
            _LOGGER.debug("miIO handshake failed")
            self._discovered = False
            return False
        finally:
            datagram.close()
        if len(data) < _HANDSHAKE_MIN_LENGTH:
            self._discovered = False
            return False
        self._device_id = struct.unpack(">I", data[8:12])[0]
        self._stamp = struct.unpack(">I", data[12:16])[0]
        self._discovered = True
        return True

    def send(
        self,
        method: str,
        parameters: object | None = None,
        retry_count: int = _SEND_RETRIES,
    ) -> object | None:
        """Send one property call. None means the cloud path should be used."""
        # A missing result is a failed local attempt, not a successful empty write.
        # The Dreame protocol falls through to cloud when this returns None.
        attempts = retry_count + 1
        for _attempt in range(attempts):
            if not self._discovered and not self.probe():
                continue
            response = self._exchange(method, parameters)
            if response is not None:
                return response
            self._discovered = False
        return None

    def _open(self) -> socket.socket:
        if self._socket_factory is None:
            datagram = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            datagram = self._socket_factory()
        datagram.settimeout(self._timeout)
        return datagram

    def _exchange(self, method: str, parameters: object | None) -> object | None:
        with self._lock:
            self._request_id = (
                1 if self._request_id >= _MAX_REQUEST_ID else self._request_id + 1
            )
            request_id = self._request_id
            self._stamp += 1
            stamp = self._stamp
            device_id = self._device_id
        params: object = [] if parameters is None else parameters
        request = {"id": request_id, "method": method, "params": params}
        encrypted = _aes_encrypt(json.dumps(request).encode(), self._key, self._iv)
        length = _HEADER_SIZE + len(encrypted)
        header = (
            struct.pack(">HH", _MIIO_MAGIC, length)
            + _HEADER_PADDING
            + struct.pack(">II", device_id, stamp)
        )
        checksum = hashlib.md5(header + self._token + encrypted).digest()
        packet = header + checksum + encrypted
        datagram = self._open()
        try:
            datagram.sendto(packet, (self._host, _MIIO_PORT))
            response, _address = datagram.recvfrom(_RESPONSE_BUFFER)
        except OSError:
            _LOGGER.debug("miIO property request failed")
            self._discovered = False
            return None
        finally:
            datagram.close()
        if len(response) <= _HEADER_SIZE:
            return None
        decrypted = _aes_decrypt(response[_HEADER_SIZE:], self._key, self._iv)
        if decrypted is None:
            return None
        try:
            result = json.loads(decrypted)
        except json.JSONDecodeError:
            return None
        if len(response) >= _HEADER_FIELDS:
            response_stamp = struct.unpack(">I", response[12:16])[0]
            if response_stamp > 0:
                self._stamp = response_stamp
        if not isinstance(result, dict):
            return None
        if "error" in result:
            _LOGGER.debug("miIO property request was rejected")
            return None
        if "result" in result:
            return result["result"]
        return result
