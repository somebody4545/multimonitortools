# setBrightness.py

import os
import time
import requests
import asyncio
import dotenv
import json
import screen_brightness_control as sbc
# from screeninfo import get_monitors # Removed as we will use sbc.list_monitors()


dotenv.load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")

started = False
current_setting = "not set"
cached_sunrise = None
cached_sunset = None
config_file = "monitors.json"

def load_config():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def calculate_brightness(monitor_id, target_val):
    config = load_config()
    if monitor_id not in config or "curve" not in config[monitor_id]:
        return target_val
    
    curve = config[monitor_id]["curve"]
    # Sort points by input value
    curve.sort(key=lambda x: x["input"])
    
    # Handle out of bounds
    if target_val <= curve[0]["input"]:
        return curve[0]["output"]
    if target_val >= curve[-1]["input"]:
        return curve[-1]["output"]
    
    # Interpolate
    for i in range(len(curve) - 1):
        test_point = curve[i]
        next_point = curve[i+1]
        if test_point["input"] <= target_val <= next_point["input"]:
            range_val = next_point["input"] - test_point["input"]
            if range_val == 0: return test_point["output"]
            factor = (target_val - test_point["input"]) / range_val
            return int(test_point["output"] + factor * (next_point["output"] - test_point["output"]))
            
    return target_val


async def start():
    global started, cached_sunrise, cached_sunset
    started = True

    location = get_setting("location", "seattle")
    # direction = "east" # Direction logic seems incomplete/unused in original code or hardcoded. leaving as is or making configurable if needed.
    # For now, let's just use the location. Redundant direction var? 
    # The original code had direction="east" hardcoded.
    direction = "east" 


    while started:
        if cached_sunrise is None or cached_sunset is None or time.time() > cached_sunset:
            # Fetch the sunrise and sunset times only once per day
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OWM_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            cached_sunrise = data["sys"]["sunrise"]
            cached_sunset = data["sys"]["sunset"]

        now = time.time()

        # Adjust brightness based on time of day
        if cached_sunrise < now < cached_sunset:
            if direction == "always lit":
                brightDay()
            elif direction == "always dim":
                dimDay()
            else:
                midday = (cached_sunrise + cached_sunset) / 2
                if cached_sunrise < now < midday:
                    if direction == "east":
                        brightDay()
                    else:
                        dimDay()
                else:
                    if direction == "west":
                        brightDay()
                    else:
                        dimDay()

        else:
            if now > cached_sunrise - get_setting("sunrise_offset", 3600) or now < cached_sunset + get_setting("sunrise_offset", 3600):
                barelyNight()
            else:
                midNight()

        await asyncio.sleep(get_setting("update_interval", 120))  # Non-blocking sleep for configured interval


def get_setting(key, default):
    config = load_config()
    if "settings" not in config:
        return default
    return config["settings"].get(key, default)

def update_setting(key, value):
    config = load_config()
    if "settings" not in config:
        config["settings"] = {}
    config["settings"][key] = value
    save_config(config)

def brightDay():
    global current_setting
    val = get_setting("bright_day", 100)
    set_brightness_for_monitors(val, "bright day")

def dimDay():
    global current_setting
    val = get_setting("dim_day", 50)
    set_brightness_for_monitors(val, "dim day")

def barelyNight():
    global current_setting
    val = get_setting("barely_night", 35)
    set_brightness_for_monitors(val, "barely night")

def midNight():
    global current_setting
    val = get_setting("midnight", 25)
    set_brightness_for_monitors(val, "midnight")

def set_brightness_for_monitors(brightness, setting):
    global current_setting
    monitors = sbc.list_monitors()
    for monitor in monitors:
        val = calculate_brightness(monitor, brightness)
        try:
            sbc.set_brightness(val, display=monitor)
        except Exception as e:
            print(f"Error setting brightness for {monitor}: {e}")
    current_setting = setting


async def stop():
    global started, current_setting
    started = False
    current_setting = "not set"

def get_monitors_friendly():
    return sbc.list_monitors()

def get_current_setting():
    return current_setting

def force_set(setting):
    asyncio.run(stop())
    monitors = sbc.list_monitors()
    for monitor in monitors:
        val = calculate_brightness(monitor, setting)
        try:
            sbc.set_brightness(val, display=monitor)
        except Exception as e:
            print(f"Error setting brightness for {monitor}: {e}")

