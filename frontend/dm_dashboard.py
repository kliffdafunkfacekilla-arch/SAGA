from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLabel, QTabWidget, QWidget, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

class DMDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("S.A.G.A. - DM Dashboard (AI X-Ray)")
        self.setGeometry(150, 150, 900, 700)
        self.setStyleSheet("background-color: #1a1a1a; color: #00ff00; font-family: Consolas, monospace;")
        
        main_layout = QVBoxLayout(self)
        
        header = QLabel("DM DEBUG TERMINAL")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff4444; border-bottom: 2px solid #555; padding-bottom: 5px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #333; color: white; padding: 8px; }
            QTabBar::tab:selected { background: #4444ff; }
            QTabWidget::pane { border: 1px solid #444; }
        """)
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: AI I/O LOGS ---
        self.io_tab = QWidget()
        io_layout = QVBoxLayout(self.io_tab)
        
        io_layout.addWidget(QLabel("STT Input (Player Intent):"))
        self.stt_log = QTextEdit()
        self.stt_log.setReadOnly(True)
        self.stt_log.setStyleSheet("background-color: #000; border: 1px solid #00ff00;")
        self.stt_log.setMaximumHeight(80)
        io_layout.addWidget(self.stt_log)
        
        io_layout.addWidget(QLabel("LLM Prompt & Director Reasoning:"))
        self.llm_log = QTextEdit()
        self.llm_log.setReadOnly(True)
        self.llm_log.setStyleSheet("background-color: #000; border: 1px solid #00ff00;")
        io_layout.addWidget(self.llm_log)
        
        self.tabs.addTab(self.io_tab, "AI Logs (I/O)")
        
        # --- TAB 2: WORLD & SIMULATION STATE ---
        self.sim_tab = QWidget()
        sim_layout = QVBoxLayout(self.sim_tab)
        
        self.cell_data_group = QGroupBox("Current Omnis Cell Data")
        self.cell_data_group.setStyleSheet("QGroupBox { border: 1px solid #ff4444; margin-top: 10px; }")
        cell_layout = QGridLayout()
        self.lbl_cell_id = QLabel("Cell ID: N/A")
        self.lbl_biome = QLabel("Biome: N/A")
        self.lbl_chaos = QLabel("Chaos Level: N/A")
        self.lbl_faction = QLabel("Faction: N/A")
        cell_layout.addWidget(self.lbl_cell_id, 0, 0)
        cell_layout.addWidget(self.lbl_biome, 0, 1)
        cell_layout.addWidget(self.lbl_chaos, 1, 0)
        cell_layout.addWidget(self.lbl_faction, 1, 1)
        self.cell_data_group.setLayout(cell_layout)
        sim_layout.addWidget(self.cell_data_group)
        
        sim_layout.addWidget(QLabel("Story Weaver (Active Seeds & Directives):"))
        self.weaver_log = QTextEdit()
        self.weaver_log.setReadOnly(True)
        self.weaver_log.setStyleSheet("background-color: #000; border: 1px solid #4444ff;")
        sim_layout.addWidget(self.weaver_log)
        
        self.tabs.addTab(self.sim_tab, "Simulation State")
        
        # --- TAB 3: PLAYER MECHANICS ---
        self.mech_tab = QWidget()
        mech_layout = QVBoxLayout(self.mech_tab)
        self.mech_log = QTextEdit()
        self.mech_log.setReadOnly(True)
        self.mech_log.setStyleSheet("background-color: #000; border: 1px solid #ffaa00;")
        mech_layout.addWidget(self.mech_log)
        self.tabs.addTab(self.mech_tab, "Player Mechanics")
        
    def update_dashboard(self, dm_data: dict):
        if not dm_data:
            return
            
        # Update IO
        stt = dm_data.get("last_intent", "")
        if stt: self.stt_log.setText(stt)
        
        llm = dm_data.get("last_prompt", "")
        if llm: self.llm_log.setText(llm)
        
        # Update Sim
        cell = dm_data.get("cell_data", {})
        if cell:
            self.lbl_cell_id.setText(f"Cell ID: {cell.get('id', 'Unknown')}")
            self.lbl_biome.setText(f"Biome: {cell.get('biome', 'Unknown')}")
            self.lbl_chaos.setText(f"Chaos Level: {cell.get('chaos', 0):.2f}")
            self.lbl_faction.setText(f"Faction: {cell.get('faction', 'None')}")
            
        seeds = dm_data.get("active_seeds", [])
        seed_txt = "ACTIVE REACTIVE SEEDS:\n"
        for s in seeds:
            seed_txt += f"- [{s.get('seed_id')}] {s.get('subtle_description')}\n"
        seed_txt += f"\nCURRENT PLOT OBJECTIVE: {dm_data.get('current_quest', 'Explore')}"
        self.weaver_log.setText(seed_txt)
        
        # Update Mechanics
        char = dm_data.get("character", {})
        if char:
            mech_txt = f"NAME: {char.get('name')}\nHP: {char.get('current_hp')}/{char.get('max_hp')}\n\nSTATS:\n"
            for k, v in char.get("stats", {}).items():
                mech_txt += f"  {k}: {v}\n"
            self.mech_log.setText(mech_txt)
