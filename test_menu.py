import sys
from PyQt6.QtWidgets import QApplication, QMenu, QWidget
app = QApplication(sys.argv)
w = QWidget()
m = QMenu(w)
try:
    m.addAction("Test", lambda: print("OK"))
    print("SUCCESS: addAction(str, callable) works!")
except Exception as e:
    print(f"FAILED: {e}")
