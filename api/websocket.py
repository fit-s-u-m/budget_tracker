from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept(
            headers=[(b"access-control-allow-origin", b"*")]
        )
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

def connect_websocket_app(app: FastAPI):

    @app.websocket("/ws/transactions")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                print(f"Received: {data}")
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            print("Client disconnected")
