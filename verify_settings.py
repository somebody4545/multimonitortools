import setBrightness as sb
import json
import os

def test_settings():
    print("Testing Settings...")
    
    # 1. Test Defaults
    assert sb.get_setting("location", "default") == "default" # Should be missing initially in clean test
    assert sb.get_setting("bright_day", 100) == 100
    
    # 2. Test Update
    sb.update_setting("location", "New York")
    sb.update_setting("bright_day", 95)
    sb.update_setting("direction", "always lit")
    sb.update_setting("update_interval", 60)
    
    # 3. Test Persistence
    config = sb.load_config()
    assert config["settings"]["location"] == "New York"
    assert config["settings"]["bright_day"] == 95
    assert config["settings"]["direction"] == "always lit"
    assert config["settings"]["update_interval"] == 60
    
    # 4. Test Retrieval
    assert sb.get_setting("location", "fail") == "New York"
    assert sb.get_setting("bright_day", 0) == 95
    
    print("PASS")

if __name__ == "__main__":
    # Backup
    if os.path.exists("monitors.json"):
        os.rename("monitors.json", "monitors.json.bak")
        
    try:
        test_settings()
    finally:
        # Restore
        if os.path.exists("monitors.json.bak"):
            if os.path.exists("monitors.json"):
                os.remove("monitors.json")
            os.rename("monitors.json.bak", "monitors.json")

    print("All Settings Tests Passed")
