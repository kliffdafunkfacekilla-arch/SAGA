"""
Provides the MapCanvas and BattleMapCanvas components for the left-hand panel of the VTT.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QLineEdit, QGraphicsView, 
                             QGraphicsScene, QMenu, QGraphicsEllipseItem, QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem)
from PyQt6.QtCore import Qt, pyqtSlot, QRectF, QTimer
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter

from beta_build.ui.sprite_manager import SpriteManager
from beta_build.ui.hud import CharacterHUD, StoryTracker

class TokenItem(QGraphicsEllipseItem):
    """Dynamic map token representing an entity (player, monster, etc)."""
    def __init__(self, x, y, size, color, name, uuid, tags=None, parent=None):
        super().__init__(0, 0, size, size, parent)
        self.setPos(x * size, y * size)
        self.uuid = uuid
        self.name = name
        self.tags = tags or []
        
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(QColor("white"), 2))
        
        # Add label for name
        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QColor("white"))
        self.label.setPos(0, -15)
        
        self.original_color = QColor(color)
        self.is_dead = False

    def move_to_grid(self, x, y, size):
        if not self.is_dead:
            self.setPos(x * size, y * size)
            
    def flash_damage(self):
        if self.is_dead: return
        self.setBrush(QBrush(QColor("white")))
        # Revert color after 150ms
        QTimer.singleShot(150, lambda: self.setBrush(QBrush(self.original_color)) if not self.is_dead else None)
        
    def set_dead(self):
        self.is_dead = True
        self.setBrush(QBrush(QColor("#333333")))
        self.setPen(QPen(QColor("#555555"), 1))
        self.label.setDefaultTextColor(QColor("#555555"))
        # Move to background so living tokens walk over it
        self.setZValue(-1)

class BattleMapCanvas(QGraphicsView):
    """
    Renders the local battle map dynamically.
    Optimized 2D Engine using QGraphicsScene.
    """
    def __init__(self, bus):
        super().__init__()
        self.bus = bus
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setMinimumHeight(350)
        self.setBackgroundBrush(QBrush(QColor("#0a0a0a")))
        
        self.tile_size = 32
        self.entities = {} # Map of UUID -> TokenItem
        
        # Enable dragging/panning
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Draws an infinite mathematical grid."""
        super().drawBackground(painter, rect)
        
        left = int(rect.left()) - (int(rect.left()) % self.tile_size)
        top = int(rect.top()) - (int(rect.top()) % self.tile_size)
        
        grid_pen = QPen(QColor("#2a2a2a"), 1, Qt.PenStyle.SolidLine)
        painter.setPen(grid_pen)
        
        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += self.tile_size
            
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += self.tile_size

    def wheelEvent(self, event):
        """Zoom in/out with mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)

    def spawn_entity(self, uuid: str, x: int, y: int, color: str, name: str, tags: list = None):
        if uuid in self.entities:
            self.move_entity(uuid, x, y)
            return
            
        token = TokenItem(x, y, self.tile_size, color, name, uuid, tags)
        self.scene.addItem(token)
        self.entities[uuid] = token
        
    def move_entity(self, uuid: str, x: int, y: int):
        if uuid in self.entities:
            self.entities[uuid].move_to_grid(x, y, self.tile_size)
            
    def remove_entity(self, uuid: str):
        if uuid in self.entities:
            token = self.entities.pop(uuid)
            self.scene.removeItem(token)
            
    def damage_entity(self, uuid: str):
        if uuid in self.entities:
            self.entities[uuid].flash_damage()
            
    def kill_entity(self, uuid: str):
        if uuid in self.entities:
            self.entities[uuid].set_dead()

    def load_generated_payload(self, payload: dict):
        """Loads a generated grid and entities from the WorldGenWorker."""
        self.scene.clear()
        self.entities.clear()
        
        grid = payload.get("grid", [])
        self.grid_data = grid
        for y, row in enumerate(grid):
            for x, node in enumerate(row):
                # node is a Terrain Node dict
                node_type = node.get("type", "floor") if isinstance(node, dict) else ("wall" if node == 1 else ("water" if node == 2 else "floor"))
                if node_type in ("wall", "obstacle"):
                    rect = QGraphicsRectItem(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    rect.setBrush(QBrush(QColor("#444444")))
                    rect.setPen(QPen(Qt.PenStyle.NoPen))
                    self.scene.addItem(rect)
                elif node_type == "water":
                    rect = QGraphicsRectItem(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    rect.setBrush(QBrush(QColor("#113355")))
                    rect.setPen(QPen(Qt.PenStyle.NoPen))
                    self.scene.addItem(rect)
                    
        # Add player at center
        width = payload.get("width", 40)
        height = payload.get("height", 40)
        self.spawn_entity("player_1", width // 2, height // 2, "gold", "Wanderer")
        
        for ent in payload.get("entities", []):
            self.spawn_entity(
                uuid=ent.get("uuid"),
                x=ent.get("x", 0),
                y=ent.get("y", 0),
                color="red",
                name=ent.get("name", "Unknown"),
                tags=ent.get("tags", [])
            )

    def mousePressEvent(self, event):
        """Handle right/left clicks to open contextual interaction menus."""
        if event.button() == Qt.MouseButton.RightButton or event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            clicked_x = int(scene_pos.x() // self.tile_size)
            clicked_y = int(scene_pos.y() // self.tile_size)
            
            self.show_context_menu(event.globalPosition().toPoint(), clicked_x, clicked_y)
        else:
            super().mousePressEvent(event)
            
    def show_context_menu(self, global_pos, gx, gy):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #333; color: white; border: 1px solid #555; } QMenu::item:selected { background-color: #555; }")
        
        clicked_entity = None
        for uuid, token in self.entities.items():
            tx = int(token.pos().x() // self.tile_size)
            ty = int(token.pos().y() // self.tile_size)
            if tx == gx and ty == gy:
                clicked_entity = token
                break
                
        if clicked_entity:
            name = clicked_entity.name
            menu.addAction(f"Interact with {name}", lambda: self._send_intent(f"interact with {name}"))
            menu.addAction(f"Examine {name}", lambda: self._send_intent(f"examine {name}"))
            menu.addAction(f"Attack {name}", lambda: self._send_intent(f"attack {name}"))
        else:
            menu.addAction("Move Here", lambda: self._send_intent(f"move to {gx} {gy}"))
            menu.addAction("Examine Area", lambda: self._send_intent("examine area"))
            
        menu.exec(global_pos)
        
    def _send_intent(self, intent_str):
        self.bus.publish("PLAYER_ACTION_UI_INJECT", {"intent": intent_str})


class MapCanvas(QWidget):
    """
    The main game view housing the BattleMap, Chat Log, Input Field, and Right-hand HUD.
    """
    def __init__(self, bus):
        super().__init__()
        self.bus = bus
        
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        
        self.title = QLabel("S.A.G.A. Engine VTT (Beta Async)")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #44FF44; margin-bottom: 5px;")
        
        self.battle_map = BattleMapCanvas(self.bus)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #222;
                color: #DDD;
                font-family: monospace;
                font-size: 14px;
                padding: 10px;
                border: 2px solid #555;
            }
        """)
        self.log_view.append(">> Engine Initialized. Map Cluster Loaded.\n")
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("State your intent (e.g. 'I walk north' or 'I attack')")
        self.input_field.setStyleSheet("padding: 10px; font-size: 16px; background-color: #333; color: white; border: 1px solid #777;")
        self.input_field.returnPressed.connect(self._on_action_submitted)
        
        self.btn_submit = QPushButton("Execute")
        self.btn_submit.setStyleSheet("padding: 10px; font-size: 16px; background-color: #555; color: white; font-weight: bold;")
        self.btn_submit.clicked.connect(self._on_action_submitted)
        
        self.btn_char = QPushButton("Character Sheet")
        self.btn_char.setStyleSheet("padding: 10px; font-size: 16px; background-color: #335577; color: white; font-weight: bold;")
        self.btn_char.clicked.connect(lambda: self.bus.publish("UI_OPEN_CHAR_MANAGEMENT"))
        
        self.btn_stealth = QPushButton("Stealth: OFF")
        self.btn_stealth.setCheckable(True)
        self.btn_stealth.setStyleSheet("padding: 10px; font-size: 16px; background-color: #222; color: #888; border: 1px solid #555;")
        self.btn_stealth.toggled.connect(self._on_stealth_toggled)
        
        self.btn_dm = QPushButton("DM Dashboard")
        self.btn_dm.setStyleSheet("padding: 10px; font-size: 16px; background-color: #551111; color: #ff5555; font-weight: bold; border: 1px solid #ff5555;")
        self.btn_dm.clicked.connect(lambda: self.bus.publish("OPEN_DM_DASHBOARD"))
        
        self.btn_camp = QPushButton("Camp (Long Rest)")
        self.btn_camp.setStyleSheet("padding: 10px; font-size: 16px; background-color: #773333; color: white; font-weight: bold;")
        self.btn_camp.clicked.connect(lambda: self.bus.publish("UI_LONG_REST"))
        
        self.btn_mic = QPushButton("🎙️ Mic: OFF")
        self.btn_mic.setCheckable(True)
        self.btn_mic.setStyleSheet("padding: 10px; font-size: 16px; background-color: #222; color: #888; border: 1px solid #555;")
        self.btn_mic.toggled.connect(self._on_mic_toggled)

        input_layout.addWidget(self.btn_mic)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_submit)
        input_layout.addWidget(self.btn_char)
        input_layout.addWidget(self.btn_stealth)
        input_layout.addWidget(self.btn_dm)
        input_layout.addWidget(self.btn_camp)
        
        left_layout.addWidget(self.title)
        left_layout.addWidget(self.battle_map)
        left_layout.addWidget(self.log_view)
        left_layout.addLayout(input_layout)
        
        right_panel = QVBoxLayout()
        self.hud = CharacterHUD()
        self.story_tracker = StoryTracker()
        right_panel.addWidget(self.hud)
        right_panel.addWidget(self.story_tracker)
        right_panel.addStretch()
        
        main_layout.addLayout(left_layout, stretch=4)
        main_layout.addLayout(right_panel, stretch=1)
        self.setLayout(main_layout)
        
        self.bus.subscribe("MAP_RENDER", self._on_map_render)
        self.bus.subscribe("HUD_UPDATE", self._on_hud_update)
        self.bus.subscribe("PLAYER_ACTION_UI_INJECT", self._handle_ui_inject)
        
        self.bus.subscribe("SPAWN_ENTITY", self._on_spawn_entity)
        self.bus.subscribe("MOVE_ENTITY", self._on_move_entity)
        self.bus.subscribe("REMOVE_ENTITY", self._on_remove_entity)
        self.bus.subscribe("ENTITY_DAMAGED", self._on_entity_damaged)
        self.bus.subscribe("ENTITY_DIED", self._on_entity_died)
        self.bus.subscribe("MAP_PAYLOAD_READY", self._on_map_payload_ready)

    def _on_spawn_entity(self, payload):
        self.battle_map.spawn_entity(
            uuid=payload.get("uuid"),
            x=payload.get("x", 0),
            y=payload.get("y", 0),
            color=payload.get("color", "red"),
            name=payload.get("name", "Unknown"),
            tags=payload.get("tags", [])
        )

    def _on_move_entity(self, payload):
        self.battle_map.move_entity(
            uuid=payload.get("uuid"),
            x=payload.get("x", 0),
            y=payload.get("y", 0)
        )

    def _on_remove_entity(self, payload):
        self.battle_map.remove_entity(payload.get("uuid"))

    def _on_entity_damaged(self, payload):
        self.battle_map.damage_entity(payload.get("uuid"))
        
    def _on_entity_died(self, payload):
        self.battle_map.kill_entity(payload.get("uuid"))

    def _on_map_payload_ready(self, payload):
        name = payload.get("name", "Unknown")
        self.title.setText(f"S.A.G.A. Engine VTT (Beta Async) - {name}")
        self.battle_map.load_generated_payload(payload)

    def _on_map_render(self, payload):
        # Kept for backward compatibility if we still want to read legacy grids,
        # but the map handles its own infinite grid now.
        pass
        
    def _on_hud_update(self, payload):
        if "character" in payload:
            self.hud.update_stats(payload["character"])
        if "dm_data" in payload:
            quest = payload["dm_data"].get("current_quest", "")
            seeds = payload["dm_data"].get("active_seeds", [])
            self.story_tracker.update_story(quest, seeds)
        
    def _on_stealth_toggled(self, checked):
        if checked:
            self.btn_stealth.setText("Stealth: ON")
            self.btn_stealth.setStyleSheet("padding: 10px; font-size: 16px; background-color: #44FF44; color: black; font-weight: bold;")
            self.bus.publish("UI_TOGGLE_STEALTH", {"stealth": True})
            self.log_view.append("\n[SYS] You have entered Stealth Mode. Movement and actions will use Finesse.")
        else:
            self.btn_stealth.setText("Stealth: OFF")
            self.btn_stealth.setStyleSheet("padding: 10px; font-size: 16px; background-color: #222; color: #888; border: 1px solid #555;")
            self.bus.publish("UI_TOGGLE_STEALTH", {"stealth": False})
            self.log_view.append("\n[SYS] You have left Stealth Mode.")
            
    def _on_mic_toggled(self, checked):
        if checked:
            self.btn_mic.setText("🎙️ Mic: ON")
            self.btn_mic.setStyleSheet("padding: 10px; font-size: 16px; background-color: #FF4444; color: white; font-weight: bold;")
            self.bus.publish("UI_TOGGLE_MIC", {"active": True})
        else:
            self.btn_mic.setText("🎙️ Mic: OFF")
            self.btn_mic.setStyleSheet("padding: 10px; font-size: 16px; background-color: #222; color: #888; border: 1px solid #555;")
            self.bus.publish("UI_TOGGLE_MIC", {"active": False})

    def _handle_ui_inject(self, payload):
        intent = payload.get("intent", "")
        if intent:
            # Re-publish to the main app to trigger the LLM
            self.bus.publish("EXECUTE_INTENT", {"intent": intent})

    def _on_action_submitted(self):
        intent = self.input_field.text().strip()
        if not intent: return
        self.input_field.clear()
        
        self.log_view.append(f"\n<b>Player:</b> {intent}")
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
        
        self.bus.publish("EXECUTE_INTENT", {"intent": intent})

    # --- Signals from Workers ---
    @pyqtSlot(str)
    def on_token_received(self, token: str):
        # Insert token into log for typewriter effect
        cursor = self.log_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(token)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    @pyqtSlot(str, str)
    def on_generation_complete(self, tag: str, full_text: str):
        self.log_view.append("\n")
        
    @pyqtSlot(str)
    def on_speech_recognized(self, text: str):
        self.input_field.setText(text)
        self._on_action_submitted()
        
    @pyqtSlot(str)
    def on_error(self, err: str):
        self.log_view.append(f"\n<font color='red'>[ERROR] {err}</font>\n")
