import setBrightness as sb
import json
import os

def test_config_io():
    print("Testing Config I/O...")
    test_config = {
        "test_monitor": {
            "curve": [
                {"input": 0, "output": 10},
                {"input": 50, "output": 20},
                {"input": 100, "output": 30}
            ]
        }
    }
    sb.save_config(test_config)
    loaded = sb.load_config()
    assert loaded == test_config
    print("PASS")

def test_calculation():
    print("Testing Calculation...")
    monitor_id = "test_monitor"
    
    # Points: (0,10), (50,20), (100,30)
    
    # Test Exact Points
    assert sb.calculate_brightness(monitor_id, 0) == 10
    assert sb.calculate_brightness(monitor_id, 50) == 20
    assert sb.calculate_brightness(monitor_id, 100) == 30
    
    # Test Interpolation
    # 25 is midway between 0 and 50. Output should be midway 10 and 20 -> 15.
    assert sb.calculate_brightness(monitor_id, 25) == 15
    
    # 75 is midway between 50 and 100. Output midway 20 and 30 -> 25.
    assert sb.calculate_brightness(monitor_id, 75) == 25
    
    # Test Bounds
    # Below 0 -> 10
    assert sb.calculate_brightness(monitor_id, -10) == 10
    # Above 100 -> 30
    assert sb.calculate_brightness(monitor_id, 110) == 30
    
    print("PASS")

def test_no_config():
    print("Testing No Config defaults...")
    assert sb.calculate_brightness("unknown_monitor", 50) == 50
    print("PASS")

if __name__ == "__main__":
    try:
        if os.path.exists("monitors.json"):
            os.rename("monitors.json", "monitors.json.bak")
            
        test_config_io()
        test_calculation()
        test_no_config()
        
    finally:
        if os.path.exists("monitors.json.bak"):
            if os.path.exists("monitors.json"):
                os.remove("monitors.json")
            os.rename("monitors.json.bak", "monitors.json")
    
    print("All Tests Passed")
