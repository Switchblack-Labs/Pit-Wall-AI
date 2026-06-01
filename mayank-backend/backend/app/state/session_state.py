class SessionState:
    def __init__(self):
        self.active_connections = []

    def add_connection(self, websocket):
        self.active_connections.append(websocket)

    def remove_connection(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)