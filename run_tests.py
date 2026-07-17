import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, method, url, data=None):
    print(f"\n--- Testing {name} ---")
    try:
        if method == "GET":
            res = requests.get(url, params=data)
        elif method == "POST":
            res = requests.post(url, json=data)
        
        print(f"Status Code: {res.status_code}")
        if res.status_code != 200:
            print("ERROR:")
            print(res.text)
            return False
        else:
            try:
                print("Response JSON:")
                print(res.json())
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
                print(res.text)
            return True
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def run_tests():
    success = True
    
    # 1. Test TTRPG Query
    if not test_endpoint("TTRPG Query (Local Map)", "GET", f"{BASE_URL}/api/ttrpg/query", {"location_type": "Burg", "location_id": 1, "cluster_id": 13}):
        success = False
        
    # 2. Create Character
    if not test_endpoint("Create Character", "POST", f"{BASE_URL}/api/ttrpg/create_character", {"name": "Test QA", "origin": "QA Land", "class": "Tester"}):
        success = False
        
    # 3. Test Chat (Intent Parser)
    # We pass a wait action to trigger some output without moving.
    if not test_endpoint("TTRPG Chat", "POST", f"{BASE_URL}/api/ttrpg/chat", {"player_id": 1, "message": "I look around the room."}):
        success = False

    # 4. Test Director Pulse
    if not test_endpoint("Director Pulse", "POST", f"{BASE_URL}/api/ttrpg/director_pulse", {"player_id": 1}):
        success = False
        
    # 5. Test World Tick
    if not test_endpoint("World Tick", "POST", f"{BASE_URL}/api/ttrpg/tick"):
        success = False
        
    if success:
        print("\nAll automated tests passed successfully.")
    else:
        print("\nSome tests failed. Check logs.")

if __name__ == "__main__":
    run_tests()
