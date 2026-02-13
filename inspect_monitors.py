import screen_brightness_control as sbc
import json

monitors = sbc.list_monitors()
print(json.dumps(monitors, indent=2))
