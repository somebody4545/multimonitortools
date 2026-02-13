import time
import numpy as np
from PIL import ImageGrab
from screeninfo import get_monitors


def most_frequent(a):
    # Original logic: Find most frequent item in list.
    # Optimizing this with numpy because pure python list implementation is slow.
    # Convert list to numpy array if it isn't one
    arr = np.array(a)
    # Find unique rows and counts
    unique, counts = np.unique(arr, axis=0, return_counts=True)
    # Get index of max count
    index = np.argmax(counts)
    return unique[index]

def calculate_dcr_target(monitor_index=0, step=50, lower_threshold=0, upper_threshold=255):
    try:
        monitors = get_monitors()
        if monitor_index >= len(monitors):
            return 50 # Default safe fallback
            
        monitor = monitors[monitor_index]
        monitor_x = monitor.x
        monitor_y = monitor.y
        monitor_w = monitor.width
        monitor_h = monitor.height
        
        # Grab screen
        img = ImageGrab.grab(bbox=(monitor_x, monitor_y, monitor_x + monitor_w, monitor_y + monitor_h))
        
        # Convert to numpy
        im_arr = np.array(img)
        
        # Subsample using step
        if im_arr.shape[0] < step or im_arr.shape[1] < step:
            subset = im_arr
        else:
            subset = im_arr[0::step, 0::step]
        
        # Calculate Mean Brightness
        avg_color = np.mean(subset)
        
        # Map [lower, upper] to [0, 100]
        # Clamp input to range
        clamped_input = max(lower_threshold, min(upper_threshold, avg_color))
        input_range = upper_threshold - lower_threshold
        
        if input_range <= 0:
            # Degenerate case
            if avg_color >= upper_threshold: return 100
            return 0
            
        factor = (clamped_input - lower_threshold) / input_range
        target = factor * 100
        
        return int(target)
        
    except Exception as e:
        print(f"DCR Error: {e}")
        return 50

if __name__ == "__main__":
    t = time.time()
    val = calculate_dcr_target()
    print(f"DCR Target: {val} (Values 50-100 expected)")
    print(f"Time taken: {time.time() - t:.4f}s")
