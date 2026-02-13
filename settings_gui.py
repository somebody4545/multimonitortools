import tkinter as tk
from tkinter import ttk, messagebox
import setBrightness as sb

class SettingsEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x650")
        
        self.settings = {
            "location": tk.StringVar(),
            "bright_day": tk.IntVar(),
            "dim_day": tk.IntVar(),
            "barely_night": tk.IntVar(),
            "midnight": tk.IntVar(),
            "sunrise_offset": tk.IntVar(),
            "direction": tk.StringVar(),
            "update_interval": tk.IntVar(),
            "dcr_weight": tk.IntVar(),
            "dcr_interval": tk.DoubleVar(),
            "dcr_min": tk.IntVar(),
            "dcr_max": tk.IntVar(),
            "dcr_trigger_min": tk.IntVar(),
            "dcr_trigger_max": tk.IntVar()
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
        self.settings["dcr_weight"].set(sb.get_setting("dcr_weight", 0))
        self.settings["dcr_interval"].set(sb.get_setting("dcr_interval", 1.0))
        self.settings["dcr_min"].set(sb.get_setting("dcr_min", 0))
        self.settings["dcr_max"].set(sb.get_setting("dcr_max", 100))
        self.settings["dcr_trigger_min"].set(sb.get_setting("dcr_trigger_min", 0))
        self.settings["dcr_trigger_max"].set(sb.get_setting("dcr_trigger_max", 255))







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

        # DCR
        frame_dcr = ttk.LabelFrame(self, text="Dynamic Contrast Ratio (DCR)", padding=10)
        frame_dcr.pack(fill=tk.X, **padding)
        self.create_slider(frame_dcr, "DCR Influence % (0=Off)", "dcr_weight")
        
        # DCR Interval
        frame_dcr_int = ttk.Frame(frame_dcr)
        frame_dcr_int.pack(fill=tk.X, pady=2)
        ttk.Label(frame_dcr_int, text="Update Speed (s):", width=15).pack(side=tk.LEFT)
        ttk.Scale(frame_dcr_int, from_=0.1, to=5.0, orient=tk.HORIZONTAL, variable=self.settings["dcr_interval"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(frame_dcr_int, textvariable=self.settings["dcr_interval"], width=4).pack(side=tk.LEFT)

        # Min/Max Range
        frame_dcr_range = ttk.Frame(frame_dcr)
        frame_dcr_range.pack(fill=tk.X, pady=2)
        
        # Min
        f_min = ttk.Frame(frame_dcr_range)
        f_min.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_min, text="Min:", width=5).pack(side=tk.LEFT)
        ttk.Scale(f_min, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.settings["dcr_min"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_min, textvariable=self.settings["dcr_min"], width=3).pack(side=tk.LEFT)
        
        # Max
        f_max = ttk.Frame(frame_dcr_range)
        f_max.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(f_max, text="Max:", width=5).pack(side=tk.LEFT)
        ttk.Scale(f_max, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.settings["dcr_max"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_max, textvariable=self.settings["dcr_max"], width=3).pack(side=tk.LEFT)

        # Trigger Range
        frame_dcr_trigger = ttk.Frame(frame_dcr)
        frame_dcr_trigger.pack(fill=tk.X, pady=2)
        
        # Trig Min
        f_tmin = ttk.Frame(frame_dcr_trigger)
        f_tmin.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_tmin, text="Trig Min:", width=7).pack(side=tk.LEFT)
        ttk.Scale(f_tmin, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.settings["dcr_trigger_min"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_tmin, textvariable=self.settings["dcr_trigger_min"], width=3).pack(side=tk.LEFT)
        
        # Trig Max
        f_tmax = ttk.Frame(frame_dcr_trigger)
        f_tmax.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(f_tmax, text="Trig Max:", width=7).pack(side=tk.LEFT)
        ttk.Scale(f_tmax, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.settings["dcr_trigger_max"]).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_tmax, textvariable=self.settings["dcr_trigger_max"], width=3).pack(side=tk.LEFT)




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
            sb.update_setting("dcr_weight", self.settings["dcr_weight"].get())
            sb.update_setting("dcr_interval", self.settings["dcr_interval"].get())
            sb.update_setting("dcr_min", self.settings["dcr_min"].get())
            sb.update_setting("dcr_max", self.settings["dcr_max"].get())
            sb.update_setting("dcr_trigger_min", self.settings["dcr_trigger_min"].get())
            sb.update_setting("dcr_trigger_max", self.settings["dcr_trigger_max"].get())



            
            messagebox.showinfo("Saved", "Settings saved successfully.")

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
