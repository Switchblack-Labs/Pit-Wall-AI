"""Abstract TORCS telemetry source."""

from __future__ import annotations

import abc
from typing import AsyncIterator

from app.schemas.torcs import TorcsTelemetry


class TorcsSource(abc.ABC):
    """A source of TORCS-format telemetry frames.

    Implementations yield :class:`TorcsTelemetry` frames asynchronously until
    :meth:`stop` is called. This common interface lets the ingestion layer
    treat the built-in simulator and a future live SCR bridge identically.
    """

    name: str = "base"

    @abc.abstractmethod
    def frames(self) -> AsyncIterator[TorcsTelemetry]:
        """Return an async iterator yielding telemetry frames until stopped."""

    @abc.abstractmethod
    def stop(self) -> None:
        """Signal the source to stop producing frames."""
