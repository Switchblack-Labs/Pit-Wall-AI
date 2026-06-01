from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies import get_websocket_service

router = APIRouter()


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    websocket_service = get_websocket_service()

    await websocket_service.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)