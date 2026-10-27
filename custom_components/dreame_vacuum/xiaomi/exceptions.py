"""Exceptions raised by the Xiaomi vacuum family."""

from __future__ import annotations


class XiaomiTransportException(Exception):  # noqa: N818 - core uses Exception
    """The local miIO property transport could not be built."""
