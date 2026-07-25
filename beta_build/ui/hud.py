"""
Provides the CharacterHUD and StoryTracker components for the right-hand panel of the VTT.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QProgressBar
from PyQt6.QtCore import Qt

class CharacterHUD(QFrame):
    """
    Displays the character's core stats (HP, Stamina, Focus) using pure QSS graphical elements.
    Listens for 'HUD_UPDATE' events to refresh data from the Pydantic CharacterSheet.
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #0f1115;
                border: 2px solid #2b323b;
                border-radius: 4px;
                padding: 10px;
            }
            QLabel { 
                color: #d8d8d8; 
                font-family: 'Segoe UI', serif; 
                font-weight: bold; 
                border: none; 
            }
            QProgressBar {
                background-color: #14171c;
                border: 1px solid #1a1e24;
                border-radius: 3px;
                text-align: center;
                color: white;
                font-size: 12px;
                font-weight: bold;
                height: 18px;
            }
        """)
        self.setFixedWidth(260)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Name Plate
        self.name_label = QLabel("WANDERER")
        self.name_label.setStyleSheet("font-size: 18px; color: #a49a85; letter-spacing: 2px; text-transform: uppercase;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Health Bar (Crimson)
        self.hp_label = QLabel("HEALTH")
        self.hp_label.setStyleSheet("font-size: 11px; color: #888;")
        self.hp_bar = QProgressBar()
        self.hp_bar.setStyleSheet("QProgressBar::chunk { background-color: #8b1c1c; border-radius: 2px; }")
        layout.addWidget(self.hp_label)
        layout.addWidget(self.hp_bar)
        
        # Stamina Bar (Gritty Gold/Ochre)
        self.stamina_label = QLabel("STAMINA")
        self.stamina_label.setStyleSheet("font-size: 11px; color: #888;")
        self.stamina_bar = QProgressBar()
        self.stamina_bar.setStyleSheet("QProgressBar::chunk { background-color: #b08d43; border-radius: 2px; }")
        layout.addWidget(self.stamina_label)
        layout.addWidget(self.stamina_bar)
        
        # Focus Bar (Deep Void Blue)
        self.focus_label = QLabel("FOCUS")
        self.focus_label.setStyleSheet("font-size: 11px; color: #888;")
        self.focus_bar = QProgressBar()
        self.focus_bar.setStyleSheet("QProgressBar::chunk { background-color: #244170; border-radius: 2px; }")
        layout.addWidget(self.focus_label)
        layout.addWidget(self.focus_bar)
        
        # Weapon / State info
        state_layout = QHBoxLayout()
        self.weapon_label = QLabel("Weapon: Unarmed")
        self.weapon_label.setStyleSheet("color: #a49a85; font-size: 12px;")
        
        self.trauma_label = QLabel("Trauma: 0")
        self.trauma_label.setStyleSheet("color: #ff4444; font-size: 12px;")
        
        state_layout.addWidget(self.weapon_label)
        state_layout.addStretch()
        state_layout.addWidget(self.trauma_label)
        
        layout.addLayout(state_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_stats(self, stats: dict):
        """
        Updates the HUD labels based on a serialized CharacterSheet dict.
        """
        self.name_label.setText(stats.get("name", "WANDERER").upper())
        
        # HP Update
        max_hp = stats.get('max_hp', 1)
        cur_hp = stats.get('current_hp', 0)
        self.hp_bar.setMaximum(max_hp)
        self.hp_bar.setValue(cur_hp)
        self.hp_bar.setFormat(f"{cur_hp} / {max_hp}")
        
        # Stamina Update
        max_stam = stats.get('max_stamina', 1)
        cur_stam = stats.get('active_stamina', 0)
        self.stamina_bar.setMaximum(max_stam)
        self.stamina_bar.setValue(cur_stam)
        self.stamina_bar.setFormat(f"{cur_stam} / {max_stam}")
        
        # Focus Update
        max_foc = stats.get('max_focus', 1)
        cur_foc = stats.get('active_focus', 0)
        self.focus_bar.setMaximum(max_foc)
        self.focus_bar.setValue(cur_foc)
        self.focus_bar.setFormat(f"{cur_foc} / {max_foc}")
        
        # Trauma & Weapon
        self.trauma_label.setText(f"Trauma: {stats.get('trauma_tokens', 0)}")
        
        inventory = stats.get("inventory", {})
        slots = inventory.get("slots", {})
        weapon = slots.get("weapon")
        if weapon:
            self.weapon_label.setText(f"Weapon: {weapon.get('name', 'Unknown')}")
        else:
            self.weapon_label.setText("Weapon: Unarmed")


class StoryTracker(QFrame):
    """
    Displays the current story slot/quest and any active Reactive Seeds.
    Helps the player keep track of looming consequences and narrative goals.
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #3a414c;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
            QLabel { color: #ddd; font-family: 'Segoe UI', sans-serif; border: none; }
        """)
        self.setFixedWidth(250)
        
        layout = QVBoxLayout()
        
        self.title_label = QLabel("Plot Directives")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-bottom: 5px;")
        
        self.quest_label = QTextEdit("Explore the world...")
        self.quest_label.setReadOnly(True)
        self.quest_label.setStyleSheet("background-color: #222; color: #aaa; font-style: italic; border: none; max-height: 80px;")
        
        self.seeds_title = QLabel("Looming Consequences")
        self.seeds_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff5555; margin-top: 10px;")
        
        self.seeds_log = QTextEdit("None.")
        self.seeds_log.setReadOnly(True)
        self.seeds_log.setStyleSheet("background-color: #222; color: #ff9999; border: none; max-height: 120px;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.quest_label)
        layout.addWidget(self.seeds_title)
        layout.addWidget(self.seeds_log)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_story(self, quest: str, active_seeds: list):
        """
        Updates the quest tracker and active seeds log.
        
        Args:
            quest (str): The current narrative directive.
            active_seeds (list): A list of dictionaries representing unresolved Reactive Seeds.
        """
        self.quest_label.setText(quest if quest else "Survive the Drift.")
        if not active_seeds:
            self.seeds_log.setText("The world is quiet... for now.")
        else:
            seed_text = ""
            for seed in active_seeds:
                desc = seed.get('subtle_description', '')
                urgency = seed.get('urgency_ticks', 0)
                seed_text += f"[{urgency} Ticks] {desc}\n\n"
            self.seeds_log.setText(seed_text.strip())
