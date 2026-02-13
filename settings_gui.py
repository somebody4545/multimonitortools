import tkinter as tk
from tkinter import ttk, messagebox
import setBrightness as sb

class SettingsEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x500")
        
        self.settings = {
            "location": tk.StringVar(),
            "bright_day": tk.IntVar(),
            "dim_day": tk.IntVar(),
            "barely_night": tk.IntVar(),
            "midnight": tk.IntVar(),
            "sunrise_offset": tk.IntVar(),
            "direction": tk.StringVar(),
            "update_interval": tk.IntVar()
        }

        
        self.load_current_settings()
        self.setup_ui()
        
    def load_current_settings(self):
        self.settings["location"].set(sb.get_setting("location", "seattle"))
        self.settings["bright_day"].set(sb.get_setting("bright_day", 100))
        self.settings["dim_day"].set(sb.get_setting("dim_day", 50))
        self.settings["barely_night"].set(sb.get_setting("barely_night", 35))
        self.settings["midnight"].set(sb.get_setting("midnight", 25))
        self.settings["sunrise_offset"].set(sb.get_setting("sunrise_offset", 3600))
        self.settings["direction"].set(sb.get_setting("direction", "east"))
        self.settings["update_interval"].set(sb.get_setting("update_interval", 120))



    def setup_ui(self):
        padding = {'padx': 10, 'pady': 5}
        
        # Location
        frame_loc = ttk.LabelFrame(self, text="Location (for Weather)", padding=10)
        frame_loc.pack(fill=tk.X, **padding)
        ttk.Label(frame_loc, text="City Name:").pack(side=tk.LEFT)
        ttk.Entry(frame_loc, textvariable=self.settings["location"]).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Direction
        frame_dir = ttk.LabelFrame(self, text="Window Direction", padding=10)
        frame_dir.pack(fill=tk.X, **padding)
        ttk.Combobox(frame_dir, textvariable=self.settings["direction"], 
                     values=["east", "west", "always lit", "always dim"], state="readonly").pack(fill=tk.X)


        # Brightness Levels
        frame_bright = ttk.LabelFrame(self, text="Auto-Brightness Levels (%)", padding=10)
        frame_bright.pack(fill=tk.X, **padding)
        
        self.create_slider(frame_bright, "Bright Day", "bright_day")
        self.create_slider(frame_bright, "Dim Day", "dim_day")
        self.create_slider(frame_bright, "Barely Night", "barely_night")
        self.create_slider(frame_bright, "Midnight", "midnight")

        # Offsets
        frame_offset = ttk.LabelFrame(self, text="Time Offsets (seconds)", padding=10)
        frame_offset.pack(fill=tk.X, **padding)
        ttk.Label(frame_offset, text="Sunrise/Sunset Offset:").pack(side=tk.LEFT)
        ttk.Entry(frame_offset, textvariable=self.settings["sunrise_offset"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_offset, text="Update Interval:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame_offset, textvariable=self.settings["update_interval"]).pack(side=tk.LEFT, padx=5)


        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20)
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def create_slider(self, parent, label, key):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
        ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.settings[key]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(frame, textvariable=self.settings[key], width=4).pack(side=tk.LEFT)

    def save_settings(self):
        try:
            sb.update_setting("location", self.settings["location"].get())
            sb.update_setting("bright_day", self.settings["bright_day"].get())
            sb.update_setting("dim_day", self.settings["dim_day"].get())
            sb.update_setting("barely_night", self.settings["barely_night"].get())
            sb.update_setting("midnight", self.settings["midnight"].get())
            sb.update_setting("sunrise_offset", self.settings["sunrise_offset"].get())
            sb.update_setting("direction", self.settings["direction"].get())
            sb.update_setting("update_interval", self.settings["update_interval"].get())

            
            messagebox.showinfo("Saved", "Settings saved successfully.")

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
