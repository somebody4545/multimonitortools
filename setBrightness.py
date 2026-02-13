# setBrightness.py

import os
import time
import requests
import asyncio
import dotenv
import json
import screen_brightness_control as sbc
# from screeninfo import get_monitors # Removed as we will use sbc.list_monitors()
import dcr_logic



dotenv.load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY")

started = False
current_setting = "not set"
cached_sunrise = None
cached_sunset = None
config_file = "monitors.json"

# State for time-based brightness (decoupled from actual application)
current_time_target = 50 
current_time_status = "intitializing"


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


    
    last_time_check = 0

    while started:
        update_interval = get_setting("update_interval", 120)
        dcr_interval = get_setting("dcr_interval", 1) # Default 1s for DCR
        dcr_weight = get_setting("dcr_weight", 0)

        # 1. Time-based Logic Check
        # Run if never run, or if update_interval has passed
        if last_time_check == 0 or time.time() - last_time_check > update_interval:
            last_time_check = time.time()
            
            if cached_sunrise is None or cached_sunset is None or time.time() > cached_sunset:
                # Fetch the sunrise and sunset times only once per day
                try:
                    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OWM_API_KEY}&units=metric"
                    response = requests.get(url)
                    data = response.json()
                    cached_sunrise = data["sys"]["sunrise"]
                    cached_sunset = data["sys"]["sunset"]
                except Exception as e:
                    print(f"Weather API Error: {e}") 
                    if cached_sunrise is None: 
                        cached_sunrise = time.time() - 3600 # Fake day
                        cached_sunset = time.time() + 3600

            now = time.time()

            # Adjust brightness based on time of day (Updates current_time_target)
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

        # 2. Mixing Logic (Moved to per-monitor application)
        status_text = current_time_status
        if dcr_weight > 0:
             status_text += f" + DCR (Mix: {dcr_weight}%)"

        # 3. Apply
        set_brightness_for_monitors(current_time_target, status_text)


        # 4. Sleep
        if dcr_weight > 0:
            await asyncio.sleep(dcr_interval)
        else:
            await asyncio.sleep(min(update_interval, 5))


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
    global current_time_target, current_time_status
    current_time_target = get_setting("bright_day", 100)
    current_time_status = "bright day"

def dimDay():
    global current_time_target, current_time_status
    current_time_target = get_setting("dim_day", 50)
    current_time_status = "dim day"

def barelyNight():
    global current_time_target, current_time_status
    current_time_target = get_setting("barely_night", 35)
    current_time_status = "barely night"

def midNight():
    global current_time_target, current_time_status
    current_time_target = get_setting("midnight", 25)
    current_time_status = "midnight"

def set_brightness_for_monitors(base_brightness, setting):
    global current_setting
    monitors = sbc.list_monitors()
    
    dcr_weight = get_setting("dcr_weight", 0)
    
    for i, monitor in enumerate(monitors):
        final_target = base_brightness
        
        if dcr_weight > 0:
             # Calculate DCR for THIS monitor
             trig_min = get_setting("dcr_trigger_min", 0)
             trig_max = get_setting("dcr_trigger_max", 255)
             
             # Assuming monitor index `i` matches `screeninfo` order used in dcr_logic
             dcr_val = dcr_logic.calculate_dcr_target(monitor_index=i, lower_threshold=trig_min, upper_threshold=trig_max)

             # Apply Min/Max Clamping
             dcr_min = get_setting("dcr_min", 0)
             dcr_max = get_setting("dcr_max", 100)
             dcr_val = max(dcr_min, min(dcr_max, dcr_val))

             weight = dcr_weight / 100.0
             mixed_val = (base_brightness * (1 - weight)) + (dcr_val * weight)
             final_target = int(mixed_val)
        
        val = calculate_brightness(monitor, final_target)
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

