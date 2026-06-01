"""TORCS streaming service.

Mirrors the existing ``DemoService`` async-task pattern (a ``start()`` loop and a
``stop()`` flag) but drives the richer TORCS pipeline. By default it uses the
built-in :class:`SimulatedTorcsSource` so the feature works end-to-end with no
TORCS install; pass ``mode="live"`` to use :class:`LiveTorcsSource`.

Lifecycle is guarded so ``/api/torcs/start`` is idempotent and the loop cancels
cleanly on ``/api/torcs/stop`` or application shutdown.
"""

from __future__ import annotations

from typing import Optional

from app.integrations.torcs.ingest import TorcsIngestor
from app.integrations.torcs.live_source import LiveTorcsSource
from app.integrations.torcs.simulator_source import SimulatedTorcsSource
from app.integrations.torcs.source import TorcsSource
from app.utils.logger import logger


class TorcsService:
    def __init__(self, ingestor: TorcsIngestor) -> None:
        self.ingestor = ingestor
        self._source: Optional[TorcsSource] = None
        self.running = False

    def _make_source(self, mode: str, **kwargs) -> TorcsSource:
        if mode == "live":
            return LiveTorcsSource(
                host=kwargs.get("host", "127.0.0.1"),
                port=kwargs.get("port", 3001),
            )
        return SimulatedTorcsSource(
            seed=kwargs.get("seed"),
            total_laps=kwargs.get("total_laps", 58),
        )

    async def start(self, mode: str = "simulated", **kwargs) -> None:
        if self.running:
            logger.info("TORCS source already running; ignoring start.")
            return

        self._source = self._make_source(mode, **kwargs)
        self.running = True
        logger.info("TORCS source starting (mode=%s).", self._source.name)

        try:
            async for frame in self._source.frames():
                if not self.running:
                    break
                await self.ingestor.ingest_frame(frame)
        except Exception as exc:  # noqa: BLE001 - log and stop cleanly
            logger.error("TORCS streaming error: %s", exc)
        finally:
            self.running = False
            logger.info("TORCS source stopped.")

    def stop(self) -> None:
        self.running = False
        if self._source is not None:
            self._source.stop()
