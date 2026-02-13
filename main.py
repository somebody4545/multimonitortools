# main.py

import asyncio
import setBrightness as sb
import time
import tkinter as tk
import threading
import screen_brightness_control as sbc
import curve_editor
import settings_gui



started = False
ver = "0.0.2"

start_button = None
stop_button = None
brightness_label = None
brightness_slider = None

# Function to run setBrightness.start() asynchronously
async def run_brightness():
    await sb.start()

# Wrapper function to run asyncio tasks in a separate thread
def start_brightness():
    asyncio.run(run_brightness())

# Wrapper function to run asyncio tasks in a separate thread
def stop_brightness():
    asyncio.run(sb.stop())

# Start action - starts the brightness thread
def start_action():
    global started, start_button, stop_button, brightness_slider
    if not started:
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        brightness_slider.config(state=tk.DISABLED)
        started = True
        threading.Thread(target=start_brightness, daemon=True).start()

# Stop action - stops the brightness thread
def stop_action():
    global started, start_button, stop_button
    if started:
        stop_button.config(state=tk.DISABLED)
        start_button.config(state=tk.NORMAL)
        brightness_slider.config(state=tk.NORMAL)
        started = False
        threading.Thread(target=stop_brightness, daemon=True).start()

# Function to regularly update the current brightness setting
def update_brightness_label():
    global brightness_label
    current_brightness = sb.get_current_setting()  # Get current brightness setting
    screen_brightness = sbc.get_brightness()
    if screen_brightness:
        avg_brightness = int(sum(screen_brightness) / len(screen_brightness))
        brightness_label.config(text=f"Current Brightness: {current_brightness} ({avg_brightness}%)")
        
        # Sync slider if strictly not interacting? 
        # Simple approach: Update slider to match actual brightness
        # This allows seeing auto-brightness changes.
        # Check delta to avoid fighting minor jitter or user interaction race conditions?
        # For now, just set it. 
        if abs(brightness_slider.get() - avg_brightness) > 1:
             brightness_slider.set(avg_brightness)
    else:
        brightness_label.config(text=f"Current Brightness: {current_brightness} (N/A)")
    
    brightness_label.after(3000, update_brightness_label)  # Update every 3000 ms (3 seconds)


# Function to update brightness when the slider value is changed
def update_brightness_slider(value):
    brightness_value = int(value)
    sb.force_set(brightness_value)  # Force set the brightness value immediately

def open_curve_editor():
    # Helper to open the editor
    root = tk.Toplevel()
    # But wait, CurveEditor is a Toplevel. 
    # If we pass current root as parent, it works.
    # The class `CurveEditor(tk.Toplevel)` calls `super().__init__(parent)`.
    # So we just instantiate it.
    # We need the main root. 
    pass

def run():
    global start_button, stop_button, brightness_label, brightness_slider
    root = tk.Tk()
    root.title(f"mmt - {ver}")

    root.geometry("350x500")
    root.resizable(False, False)

    start_button = tk.Button(root, text="Start", command=start_action)
    stop_button = tk.Button(root, text="Stop", command=stop_action, state=tk.DISABLED)
    start_button.pack(pady=10)
    stop_button.pack(pady=10)

    curve_btn = tk.Button(root, text="Configure Curves", command=lambda: curve_editor.CurveEditor(root))
    curve_btn.pack(pady=5)

    settings_btn = tk.Button(root, text="Settings", command=lambda: settings_gui.SettingsEditor(root))
    settings_btn.pack(pady=5)



    monitors = sb.get_monitors_friendly()
    monitor_list = tk.Listbox(root, selectmode=tk.SINGLE)
    for i, monitor in enumerate(monitors):
        monitor_list.insert(i, monitor)
    monitor_list.pack(pady=10, fill=tk.X)

    brightness_label = tk.Label(root, text="Current Brightness: N/A")
    brightness_label.pack(pady=10)

    brightness_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_brightness_slider)
    brightness_slider.pack(pady=10, fill=tk.X)
    brightness_slider.set(sbc.get_brightness()[0])

    update_brightness_label()  # Start the loop to regularly update the brightness label
    root.mainloop()

if __name__ == "__main__":
    run()
