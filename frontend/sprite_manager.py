from PyQt6.QtGui import QPixmap, QColor, QPainter, QBrush, QPen
from PyQt6.QtCore import Qt
import os
import glob

class SpriteManager:
    """
    Central repository for caching, scaling, and managing 2D sprite graphics.
    """
    def __init__(self, tile_size=40):
        self.tile_size = tile_size
        self.cache = {}
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")
        
        # Ensure directory exists
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir, exist_ok=True)
            
        self._load_fallback_sprites()
        
    def _load_fallback_sprites(self):
        """Creates procedural pixmaps if files are missing."""
        self.fallback = {}
        
        # Grass Fallback
        pm = QPixmap(self.tile_size, self.tile_size)
        pm.fill(QColor(30, 100, 30))
        self.fallback["grass"] = pm
        
        # Wall Fallback
        pm_wall = QPixmap(self.tile_size, self.tile_size)
        pm_wall.fill(QColor(100, 100, 100))
        self.fallback["wall"] = pm_wall
        
        # Default Entity Fallback
        pm_ent = QPixmap(self.tile_size, self.tile_size)
        pm_ent.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm_ent)
        painter.setBrush(QBrush(QColor(200, 50, 50)))
        painter.drawEllipse(2, 2, self.tile_size-4, self.tile_size-4)
        painter.end()
        self.fallback["entity_red"] = pm_ent
        
        pm_ent_b = QPixmap(self.tile_size, self.tile_size)
        pm_ent_b.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pm_ent_b)
        painter.setBrush(QBrush(QColor(50, 50, 200)))
        painter.drawEllipse(2, 2, self.tile_size-4, self.tile_size-4)
        painter.end()
        self.fallback["entity_blue"] = pm_ent_b

    def get_sprite(self, name: str) -> QPixmap:
        """Returns the scaled QPixmap for a given name, checking cache first."""
        if name in self.cache:
            return self.cache[name]
            
        # Search the assets directory dynamically (ignores extension)
        pattern = os.path.join(self.assets_dir, f"{name}.*")
        matches = glob.glob(pattern)
        
        if matches:
            filepath = matches[0]
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.tile_size, self.tile_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.cache[name] = scaled
                return scaled
                
        # Handle miss: fallback depending on name
        if "wall" in name.lower():
            return self.fallback["wall"]
        elif "grass" in name.lower() or "floor" in name.lower():
            return self.fallback["grass"]
        elif "enemy" in name.lower():
            return self.fallback["entity_red"]
        else:
            return self.fallback["entity_blue"]
