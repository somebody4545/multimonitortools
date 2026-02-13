import tkinter as tk
from tkinter import ttk, messagebox
import setBrightness as sb
import screen_brightness_control as sbc

class CurveEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Monitor Curve Editor")
        self.geometry("600x600")
        
        self.monitors = sbc.list_monitors()
        self.current_monitor = None
        self.points = []
        self.selected_point = None
        self.drag_data = {"x": 0, "y": 0}

        
        self.setup_ui()
        
    def setup_ui(self):
        # Top frame for monitor selection
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="Select Monitor:").pack(side=tk.LEFT)
        
        self.monitor_var = tk.StringVar()
        self.monitor_combo = ttk.Combobox(top_frame, textvariable=self.monitor_var, values=self.monitors)
        self.monitor_combo.pack(side=tk.LEFT, padx=10)
        self.monitor_combo.bind("<<ComboboxSelected>>", self.on_monitor_select)
        
        self.save_btn = ttk.Button(top_frame, text="Save Curve", command=self.save_curve)
        self.save_btn.pack(side=tk.RIGHT)
        
        self.reset_btn = ttk.Button(top_frame, text="Reset Default", command=self.reset_curve)
        self.reset_btn.pack(side=tk.RIGHT, padx=5)

        # Instructions
        ttk.Label(self, text="Click to add point. Drag to move. Right-click to remove.").pack()

        # Canvas for curve
        self.canvas_size = 400
        self.canvas_margin = 30
        self.canvas = tk.Canvas(self, width=self.canvas_size + 2*self.canvas_margin, 
                                height=self.canvas_size + 2*self.canvas_margin, bg="white")
        self.canvas.pack(pady=10)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
        self.draw_grid()

        if self.monitors:
            self.monitor_combo.current(0)
            self.on_monitor_select(None)
            
    def draw_grid(self):
        self.canvas.delete("grid")
        self.canvas.delete("axis_labels")
        
        m = self.canvas_margin
        s = self.canvas_size
        
        # Draw box
        self.canvas.create_rectangle(m, m, m+s, m+s, outline="gray", tags="grid")
        
        # Grid lines
        for i in range(0, 101, 25):
            pos = i / 100 * s
            # Vertical
            self.canvas.create_line(m+pos, m, m+pos, m+s, fill="#eee", tags="grid")
            # Horizontal (y acts inverted visually but we want 0 at bottom)
            self.canvas.create_line(m, m+s-pos, m+s, m+s-pos, fill="#eee", tags="grid")
            
            # Labels
            self.canvas.create_text(m+pos, m+s+10, text=str(i), tags="axis_labels")
            self.canvas.create_text(m-15, m+s-pos, text=str(i), tags="axis_labels")

        # Axis titles
        self.canvas.create_text(m+s/2, m+s+25, text="Target Brightness (%)", tags="axis_labels")
        self.canvas.create_text(m-25, m+s/2, text="Hardware Value", angle=90, tags="axis_labels")

    def config_to_canvas(self, x, y):
        m = self.canvas_margin
        s = self.canvas_size
        canvas_x = m + (x / 100 * s)
        canvas_y = m + s - (y / 100 * s)
        return canvas_x, canvas_y

    def canvas_to_config(self, cx, cy):
        m = self.canvas_margin
        s = self.canvas_size
        x = (cx - m) / s * 100
        y = (m + s - cy) / s * 100
        return max(0, min(100, x)), max(0, min(100, y))

    def on_monitor_select(self, event):
        self.current_monitor = self.monitor_var.get()
        self.load_curve()

    def load_curve(self):
        config = sb.load_config()
        monitor_id = self.current_monitor
        
        if monitor_id in config and "curve" in config[monitor_id]:
            raw_points = config[monitor_id]["curve"]
            self.points = sorted(raw_points, key=lambda p: p["input"])
        else:
            self.points = [{"input": 0, "output": 0}, {"input": 100, "output": 100}]
            
        self.draw_curve()

    def reset_curve(self):
        self.points = [{"input": 0, "output": 0}, {"input": 100, "output": 100}]
        self.draw_curve()

    def draw_curve(self):
        self.canvas.delete("curve")
        self.canvas.delete("point")
        
        # Sort points by input
        self.points.sort(key=lambda p: p["input"])
        
        # Draw lines
        coords = []
        for p in self.points:
            cx, cy = self.config_to_canvas(p["input"], p["output"])
            coords.extend([cx, cy])
            
        if len(coords) >= 4:
            self.canvas.create_line(coords, fill="blue", width=2, tags="curve")
            
        # Draw points
        for i, p in enumerate(self.points):
            cx, cy = self.config_to_canvas(p["input"], p["output"])
            r = 4
            color = "red" if p is self.selected_point else "blue"
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, tags=("point", f"p_{i}"))

    def on_canvas_click(self, event):
        cx, cy = event.x, event.y
        m = self.canvas_margin
        s = self.canvas_size
        
        # Check if clicked near existing point
        clicked_point = None
        for p in self.points:
            px, py = self.config_to_canvas(p["input"], p["output"])
            if (cx - px)**2 + (cy - py)**2 < 100: # 10px radius
                clicked_point = p
                break
        
        if clicked_point is not None:
            self.selected_point = clicked_point
        else:
            # Add new point if inside area
            if m <= cx <= m+s and m <= cy <= m+s:
                val_x, val_y = self.canvas_to_config(cx, cy)
                new_point = {"input": val_x, "output": val_y}
                self.points.append(new_point)
                self.selected_point = new_point
        
        self.draw_curve()

    def on_canvas_drag(self, event):
        if self.selected_point is not None:
            cx, cy = event.x, event.y
            val_x, val_y = self.canvas_to_config(cx, cy)
            
            self.selected_point["input"] = val_x
            self.selected_point["output"] = val_y
            self.draw_curve()

    def on_canvas_release(self, event):
        pass 

    def on_canvas_right_click(self, event):
        cx, cy = event.x, event.y
        for p in self.points:
            px, py = self.config_to_canvas(p["input"], p["output"])
            if (cx - px)**2 + (cy - py)**2 < 100:
                if len(self.points) > 2:
                    self.points.remove(p)
                    if self.selected_point is p:
                        self.selected_point = None
                    self.draw_curve()
                break


    def save_curve(self):
        if not self.current_monitor:
            return
            
        config = sb.load_config()
        if self.current_monitor not in config:
            config[self.current_monitor] = {}
            
        # Ensure points are sorted and integral? Input/output usually integers for brightness
        # But we can store floats.
        # But calculate_brightness in setBrightness.py might expect ints or work with floats.
        # Let's round to integers for cleaner JSON.
        
        clean_points = []
        for p in self.points:
            clean_points.append({
                "input": int(round(p["input"])),
                "output": int(round(p["output"]))
            })
            
        config[self.current_monitor]["curve"] = clean_points
        sb.save_config(config)
        messagebox.showinfo("Saved", f"Curve saved for {self.current_monitor}")
        
    def run(self):
        self.mainloop()
