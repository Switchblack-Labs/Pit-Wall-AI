from fastapi import WebSocket

from app.state.session_state import SessionState
from app.utils.logger import logger


class WebSocketService:

    def __init__(self):
        self.session_state = SessionState()

    async def connect(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.session_state.add_connection(
            websocket
        )

        logger.info(
            "WebSocket connected",
            extra={
                "active_connections": len(
                    self.session_state.active_connections
                )
            }
        )

    def disconnect(
        self,
        websocket: WebSocket
    ):

        self.session_state.remove_connection(
            websocket
        )

        logger.info(
            "WebSocket disconnected",
            extra={
                "active_connections": len(
                    self.session_state.active_connections
                )
            }
        )

    async def broadcast(
        self,
        payload: dict
    ):

        if not self.session_state.active_connections:
            return

        dead_connections = []

        for connection in self.session_state.active_connections:

            try:
                await connection.send_json(
                    payload
                )

            except Exception:
                dead_connections.append(
                    connection
                )

        for dead in dead_connections:
            self.disconnect(dead)