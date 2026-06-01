"""TORCS integration layer.

Provides a TORCS-format telemetry source that streams into the existing backend
telemetry/race-state/WebSocket flow. Two source implementations share one
interface:

* :class:`~app.integrations.torcs.simulator_source.SimulatedTorcsSource` - a
  built-in generator so the full pipeline runs end-to-end with **no TORCS
  install** (the default).
* :class:`~app.integrations.torcs.live_source.LiveTorcsSource` - a plug-and-play
  interface for a real TORCS/SCR UDP server (documented in
  ``docs/torcs-integration.md``).

The integration is **additive**: it reuses the existing
``TORCSTelemetryAdapter`` and feeds ``RaceStateService`` + ``WebSocketService``
exactly like the manual telemetry endpoint, so the current telemetry flow is
unaffected.
"""

from app.integrations.torcs.ingest import TorcsIngestor
from app.integrations.torcs.live_source import LiveTorcsSource
from app.integrations.torcs.simulator_source import SimulatedTorcsSource
from app.integrations.torcs.source import TorcsSource

__all__ = [
    "TorcsSource",
    "SimulatedTorcsSource",
    "LiveTorcsSource",
    "TorcsIngestor",
]
