import json
import os
import threading
from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QCheckBox, QGroupBox, QTextEdit, QDialog, QGridLayout)
from PyQt6.QtCore import Qt
from frontend.char_creation import CharacterCreationScreen
from frontend.app import MapCanvas
from frontend.dm_dashboard import DMDashboard
from rules_engine.character_sheet import CharacterSheet
from rules_engine.inventory import Item

# We need a way to launch the Voice Engine from here
from voice_engine import VoiceEngine

def run_voice_engine(ui_callback):
    engine = VoiceEngine(ui_callback=ui_callback)
    engine.run_loop()

class MainMenuWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setStyleSheet("background-color: #1e1e1e; color: #eeeeee; font-family: Segoe UI, sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("PROJECT S.A.G.A.")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: #4caf50; margin-bottom: 50px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Buttons
        btn_style = "background-color: #333; color: white; font-size: 20px; font-weight: bold; padding: 15px; border-radius: 5px; min-width: 300px;"
        
        btn_new = QPushButton("NEW GAME")
        btn_new.setStyleSheet(btn_style)
        btn_new.clicked.connect(self.on_new_game)
        layout.addWidget(btn_new, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        
        btn_load = QPushButton("LOAD GAME")
        btn_load.setStyleSheet(btn_style)
        btn_load.clicked.connect(self.on_load_game)
        layout.addWidget(btn_load, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        
        btn_settings = QPushButton("SETTINGS")
        btn_settings.setStyleSheet(btn_style)
        btn_settings.clicked.connect(self.on_settings)
        layout.addWidget(btn_settings, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        
        btn_dm = QPushButton("LAUNCH DM DASHBOARD")
        btn_dm.setStyleSheet("background-color: #551111; color: #ff5555; font-size: 16px; font-weight: bold; padding: 10px; border-radius: 5px; min-width: 300px; border: 1px solid #ff5555;")
        btn_dm.clicked.connect(self.parent_window.open_dm_dashboard)
        layout.addWidget(btn_dm, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        
        btn_quit = QPushButton("QUIT")
        btn_quit.setStyleSheet(btn_style)
        btn_quit.clicked.connect(self.parent_window.close)
        layout.addWidget(btn_quit, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def on_new_game(self):
        self.parent_window.show_character_creation()
        
    def on_load_game(self):
        self.parent_window.start_game(is_new=False)
        
    def on_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Campaign Settings")
        self.setStyleSheet("background-color: #2a2a2a; color: white;")
        layout = QVBoxLayout(self)
        
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Story", "Normal", "Hardcore"])
        self.diff_combo.setCurrentText("Normal")
        
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["Low", "Medium", "High"])
        self.freq_combo.setCurrentText("Medium")
        
        layout.addWidget(QLabel("Difficulty:"))
        layout.addWidget(self.diff_combo)
        layout.addWidget(QLabel("Combat Frequency:"))
        layout.addWidget(self.freq_combo)
        
        self.chk_alcohol = QCheckBox("No Alcohol/Drugs")
        self.chk_gore = QCheckBox("No Gore/Gruesome Death")
        self.chk_spiders = QCheckBox("Arachnophobia (No Spiders)")
        layout.addWidget(self.chk_alcohol)
        layout.addWidget(self.chk_gore)
        layout.addWidget(self.chk_spiders)
        
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_and_close)
        layout.addWidget(btn_save)
        
    def save_and_close(self):
        filters = []
        if self.chk_alcohol.isChecked(): filters.append("alcohol, drugs")
        if self.chk_gore.isChecked(): filters.append("extreme gore, torture")
        if self.chk_spiders.isChecked(): filters.append("spiders, arachnids")
        
        settings = {
            "difficulty": self.diff_combo.currentText(),
            "combat_frequency": self.freq_combo.currentText(),
            "filters": filters
        }
        with open("campaign_settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        self.accept()

class SagaApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.A.G.A.")
        self.setGeometry(100, 100, 1280, 720)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Instantiate DM Dashboard
        self.dm_dashboard = DMDashboard(self)
        
        # Index 0: Main Menu
        self.main_menu = MainMenuWidget(self)
        self.stack.addWidget(self.main_menu)
        
        # Index 1: Character Creation wrapper
        self.char_creation_wrapper = QWidget()
        self.char_creation_wrapper.setStyleSheet("background-color: #1e1e1e; color: #eeeeee;")
        char_layout = QVBoxLayout(self.char_creation_wrapper)
        
        self.char_screen = CharacterCreationScreen()
        char_layout.addWidget(self.char_screen)
        
        start_btn = QPushButton("BEGIN JOURNEY")
        start_btn.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; font-size: 20px; padding: 15px;")
        start_btn.clicked.connect(self.on_character_finished)
        char_layout.addWidget(start_btn)
        
        self.stack.addWidget(self.char_creation_wrapper)
        
        # Index 2: Scene Viewer
        self.scene_viewer = MapCanvas(self.bus)  # Pass the event bus to the map canvas
        self.stack.addWidget(self.scene_viewer)
        
        self.stack.setCurrentIndex(0)
        
        # unified_window doesn't strictly need to connect this if it uses EventBus
        # self.scene_viewer.state_updated.connect(self._on_state_updated)

    def _on_state_updated(self, tags: dict):
        if "dm_data" in tags:
            self.dm_dashboard.update_dashboard(tags["dm_data"])
            
    def open_dm_dashboard(self):
        self.dm_dashboard.show()
        
    def show_character_creation(self):
        self.stack.setCurrentIndex(1)
        
    def on_character_finished(self):
        payload = self.char_screen.get_character_payload()
        if not payload:
            print("Please complete character creation.")
            return
            
        name = payload["name"]
        player = CharacterSheet(name=name, stats=payload["stats"])
        player.origin = payload["origin"]
        
        selected_tracks = [track for track, cb, stat in self.char_screen.selected_tracks]
        player.skills = selected_tracks
        
        if selected_tracks:
            primary_track = selected_tracks[0]
            if "Mercenary" in primary_track or "Bulwark" in primary_track:
                player.inventory.add_item(Item("Iron Claymore", "weapon", "might", 2, 2))
                player.inventory.add_item(Item("Heavy Plate", "body", "endurance", 3, 3))
            elif "Scholar" in primary_track or "Anomaly" in primary_track:
                player.inventory.add_item(Item("Scalpel", "weapon", "finesse", 1, 1))
            else:
                player.inventory.add_item(Item("Rusty Dagger", "weapon", "finesse", 1, 1))
                
        with open("player_save.json", "w") as f:
            json.dump(player.to_dict(), f, indent=4)
            
        # Make sure settings exists
        if not os.path.exists("campaign_settings.json"):
            with open("campaign_settings.json", "w") as f:
                json.dump({"difficulty": "Normal", "starting_plot": ""}, f)
                
        self.start_game(is_new=True)

    def start_game(self, is_new=True):
        # 1. Start background voice thread
        self.voice_thread = threading.Thread(
            target=run_voice_engine, 
            args=(lambda payload: self.bus.publish("HUD_UPDATE", payload),), 
            daemon=True
        )
        self.voice_thread.start()
        
        # 2. Switch to Scene Viewer
        self.stack.setCurrentIndex(2)
