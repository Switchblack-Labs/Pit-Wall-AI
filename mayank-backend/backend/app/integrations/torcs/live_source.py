"""Live TORCS / SCR telemetry source (plug-and-play interface).

This is the swap-in path for a *real* TORCS installation running the SCR
(Simulated Car Racing) patch, which exposes sensors over UDP. It implements the
same :class:`TorcsSource` interface as the simulated source, so switching is a
one-line change in the TORCS service.

It uses only the stdlib ``socket`` module and the pure-function protocol
helpers, and degrades gracefully: if no datagram arrives within the timeout it
simply continues, and on a fatal socket error it stops. Connecting a real TORCS
server is documented in ``docs/torcs-integration.md``.
"""

from __future__ import annotations

import asyncio
import socket
from datetime import datetime
from typing import AsyncIterator

from app.integrations.torcs.protocol import (
    parse_sensors,
    sensors_to_telemetry_dict,
)
from app.schemas.torcs import TorcsTelemetry
from app.utils.logger import logger


class LiveTorcsSource:
    """Reads SCR sensor datagrams from a live TORCS server over UDP."""

    name = "live"

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 3001,
        *,
        recv_timeout: float = 1.0,
        poll_seconds: float = 0.05,
    ) -> None:
        self.host = host
        self.port = port
        self.recv_timeout = recv_timeout
        self.poll_seconds = poll_seconds
        self._running = False
        self._sock: socket.socket | None = None

    def stop(self) -> None:
        self._running = False
        if self._sock is not None:
            try:
                self._sock.close()
            except Exception:  # noqa: BLE001
                pass
            self._sock = None

    def _open(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.recv_timeout)
        sock.bind((self.host, self.port))
        return sock

    def _frame_from_payload(self, payload: str) -> TorcsTelemetry | None:
        sensors = parse_sensors(payload)
        if not sensors:
            return None
        mapped = sensors_to_telemetry_dict(sensors)
        # Fields SCR does not expose directly: caller/track-model would derive
        # these; we provide safe defaults so validation passes.
        mapped.setdefault("lap", 0)
        mapped.setdefault("tire_wear", 0.0)
        mapped.setdefault("fuel", 0.0)
        mapped.setdefault("throttle", 0.0)
        mapped.setdefault("brake", 0.0)
        mapped.setdefault("track_position", 0.0)
        mapped.setdefault("rpm", 0)
        mapped.setdefault("gear", 0)
        mapped.setdefault("speed", 0.0)
        mapped["timestamp"] = datetime.utcnow()
        try:
            return TorcsTelemetry(**mapped)
        except Exception as exc:  # noqa: BLE001 - skip malformed frames
            logger.warning("Discarding malformed TORCS frame: %s", exc)
            return None

    async def frames(self) -> AsyncIterator[TorcsTelemetry]:
        self._running = True
        try:
            self._sock = self._open()
        except Exception as exc:  # noqa: BLE001
            logger.error("Could not bind TORCS UDP socket %s:%s — %s", self.host, self.port, exc)
            self._running = False
            return

        loop = asyncio.get_event_loop()
        while self._running:
            try:
                data = await loop.run_in_executor(None, self._recv)
            except Exception as exc:  # noqa: BLE001
                logger.error("TORCS recv error: %s", exc)
                break
            if data:
                frame = self._frame_from_payload(data)
                if frame is not None:
                    yield frame
            await asyncio.sleep(self.poll_seconds)

        self.stop()

    def _recv(self) -> str:
        assert self._sock is not None
        try:
            data, _ = self._sock.recvfrom(4096)
            return data.decode("utf-8", errors="ignore")
        except socket.timeout:
            return ""
