import numpy as np
from PIL import Image

def current_dcr_algo(img_arr):
    # Mimic dcr_logic.py
    # 1. Subsample
    step = 50
    # Handle small images for test
    if img_arr.shape[0] < step or img_arr.shape[1] < step:
        subset = img_arr
    else:
        subset = img_arr[0::step, 0::step]
    
    pixels = subset.reshape(-1, 3)
    
    # 2. Most Frequent
    unique, counts = np.unique(pixels, axis=0, return_counts=True)
    index = np.argmax(counts)
    mostFrequentColor = unique[index]
    
    # 3. Calculate
    avg_color = np.mean(mostFrequentColor)
    e = round((avg_color / 255) * 50)
    target = e + 50
    return target

def proposed_mean_algo(img_arr):
    # 1. Mean brightness of entire image
    avg_color = np.mean(img_arr)
    # Map 0-255 to 0-100 (or whatever range)
    # Current range is 50-100. Let's match that for comparison.
    target = (avg_color / 255) * 50 + 50
    return int(target)

def test_pattern(name, img_arr):
    current = current_dcr_algo(img_arr)
    proposed = proposed_mean_algo(img_arr)
    print(f"{name:20} | Current (Mode): {current:3} | Proposed (Mean): {proposed:3}")

# 1. Solid Black
black = np.zeros((1000, 1000, 3), dtype=np.uint8)
test_pattern("Solid Black", black)

# 2. Solid White
white = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
test_pattern("Solid White", white)

# 3. Split 50/50 Black/White
split = np.zeros((1000, 1000, 3), dtype=np.uint8)
split[:, :500] = 255 # Left white
test_pattern("Split 50/50", split)

# 4. Mostly Black with White Spot (Night mode with small window)
spot = np.zeros((1000, 1000, 3), dtype=np.uint8)
spot[400:600, 400:600] = 255 # Center white square (200x200 = 4% area)
test_pattern("Black w/ White Spot", spot)

# 5. Gradient
x = np.linspace(0, 255, 1000)
gradient = np.tile(x, (1000, 1)).astype(np.uint8)
gradient_img = np.stack((gradient, gradient, gradient), axis=2)
test_pattern("Gradient", gradient_img)
