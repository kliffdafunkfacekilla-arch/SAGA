import sys
from PyQt6.QtWidgets import QApplication
from beta_build.ui.map_view import MapCanvas
from beta_build.core.event_bus import EventBus

app = QApplication(sys.argv)
bus = EventBus()
canvas = MapCanvas(bus)
canvas.show()

# Send a fake grid
grid = []
for y in range(10):
    row = []
    for x in range(10):
        if x == 0 or x == 9 or y == 0 or y == 9:
            row.append({"tile_type": "wall"})
        else:
            row.append({"tile_type": "floor"})
    grid.append(row)

payload = {
    "name": "Test Dungeon",
    "grid": grid,
    "entities": [
        {"uuid": "goblin_1", "x": 3, "y": 3, "name": "Goblin", "tags": ["hostile"]}
    ]
}

bus.publish("MAP_PAYLOAD_READY", payload)
bus.publish("SPAWN_ENTITY", {"uuid": "player_1", "x": 5, "y": 5, "name": "Player"})

# Close after a few seconds
def close_app():
    app.quit()

import threading
threading.Timer(2.0, close_app).start()

sys.exit(app.exec())
