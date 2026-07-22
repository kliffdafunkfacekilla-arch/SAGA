import sys
from PyQt6.QtWidgets import QApplication
from frontend.unified_window import SagaApplicationWindow

def main():
    app = QApplication(sys.argv)
    
    # Show the Unified Application Window
    window = SagaApplicationWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
