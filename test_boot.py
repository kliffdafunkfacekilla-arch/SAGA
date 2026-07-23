# CRITICAL FIX: Must init llama_cpp before PyQt6
from ai_dm.director import AIDirector
GLOBAL_AI = AIDirector()

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from main_controller import SagaController

def test_boot():
    print("Testing SAGA Boot Sequence...")
    # SagaController handles QApplication inside its __init__ if needed, but let's check
    
    try:
        controller = SagaController()
        controller.start()
        print("MainController created and UI shown successfully.")
        
        # Schedule the application to close after 2 seconds
        QTimer.singleShot(2000, app.quit)
        
        print("Entering event loop. App will close automatically in 2 seconds.")
        app.exec()
        print("Boot test completed successfully with no crashes.")
    except Exception as e:
        print(f"CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_boot()
